import socket
from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain
from cbcast import CBCast

app = Flask(__name__)
nodeId = str(uuid4()).replace('-', '')
blockchain = Blockchain()
cbcast = CBCast(nodeId)
print(f"nodeId: {nodeId}")
cbcast.myip = socket.gethostbyname(socket.gethostname())
print(f"myip: {cbcast.myip}")


@app.route('/', methods=['GET'])
def hello():
    print("HELLO")
    return jsonify({}), 200


@app.route('/balance', methods=['GET'])
def balance():
    balance = blockchain.getBalance(nodeId)
    return jsonify({"balance": balance}), 200


@app.route('/mine', methods=['GET'])
def mine():
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)
    reward = 100

    blockchain.newTransaction(
        txid=str(uuid4()).replace('-', ''),
        sender="0",
        recipient=nodeId,
        amount=reward
    )

    block = blockchain.newBlock(proof)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previousHash': block['previousHash'],
    }
    broadcast("nodes/resolve", {})
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def newTransaction():
    values = request.json
    return cbcast.receive(values, _newTransaction)


@app.route('/transaction/sim/late', methods=['POST'])
def newTransactionLate():
    values = request.json
    createTransaction(values)
    broadcast("transaction/new", values, 2)
    del values["txid"]  # 新しいtxなのでtxidを削除
    response = createTransaction(values)
    broadcast("transaction/new", values, -1)
    cbcast.count[cbcast.myId] += 1
    return jsonify(response), 201


def _newTransaction(values):
    response = createTransaction(values)
    broadcast("transaction/new", values)
    return jsonify(response), 201


def createTransaction(values):
    required = ['recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    sender = values.get("sender", nodeId)
    txid = values.get("txid", str(uuid4()).replace('-', ''))
    recipient = values['recipient']
    amount = values['amount']
    index = blockchain.newTransaction(txid, sender, recipient, amount)
    if index is None:
        response = {'message': f'Transaction was already added'}
    else:
        print(f'Transaction will be added to Block {index}')
        response = {'message': f'Transaction will be added to Block {index}'}
    return response


@app.route('/id', methods=['GET'])
def getId():
    return nodeId


@app.route('/chain/', methods=['GET'])
def fullChain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/', methods=['GET'])
def getNodes():
    response = {
        "nodes": list(blockchain.nodes)
    }
    return jsonify(response), 200


@app.route('/pool/', methods=['GET'])
def getPools():
    response = {
        "tx": list(blockchain.txpool)
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def registerNodes():
    values = request.json
    return cbcast.receive(values, _registerNode)


def _registerNode(values):
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400
    for node in nodes:
        if node == f"http://{cbcast.myip}":
            continue
        blockchain.registerNode(node)
    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes),
    }
    print(f"myip: {cbcast.myip}")
    values["nodes"] = [f"http://{cbcast.myip}"]
    broadcast("nodes/register", values)
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET', 'POST'])
def consensus():
    replaced = blockchain.resolveConflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'newChain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


def broadcast(func, values, additional=1):
    cbcast.broadcast(func, values, blockchain.nodes, additional)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    # cbcast.myip = f"http://127.0.0.1:{port}"
    app.run(host='0.0.0.0', port=port, debug=True)
