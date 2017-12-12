from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain
from cbcast import CBCast

app = Flask(__name__)
nodeId = str(uuid4()).replace('-', '')
blockchain = Blockchain()
cbcast = CBCast(nodeId)
print(f"nodeId: {nodeId}")


@app.route('/', methods=['GET'])
def hello():
    return jsonify({}), 200


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
    return jsonify(response), 201


def _newTransaction(values):
    response = createTransaction(values)
    broadcast("transaction/new", values)
    return jsonify(response), 201


def createTransaction(values):
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    if "txid" not in values:
        values["txid"] = str(uuid4()).replace('-', '')
    index = blockchain.newTransaction(
        values["txid"], values['sender'], values['recipient'], values['amount'])
    if index is None:
        response = {'message': f'Transaction was already added'}
    else:
        print(f'Transaction will be added to Block {index}')
        response = {'message': f'Transaction will be added to Block {index}'}
    return response


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


@app.route('/nodes/register', methods=['POST'])
def registerNodes():
    values = request.json
    return cbcast.receive(values, _registerNode)


def _registerNode(values):
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400
    for node in nodes:
        blockchain.registerNode(node)
    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes),
    }
    values["nodes"] = [cbcast.myip]
    broadcast("nodes/register", values)
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
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
    # socket.gethostbyname(socket.gethostname())
    cbcast.myip = f"http://127.0.0.1:{port}"
    app.run(host='0.0.0.0', port=port, debug=True)
