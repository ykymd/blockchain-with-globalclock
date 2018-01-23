import socket
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain
from cbcast import CBCast
from network import Network

app = Flask(__name__)
nodeId = str(uuid4()).replace('-', '')
blockchain = Blockchain()

isLogicalGlobalClock = False
if isLogicalGlobalClock:
    cast = CBCast(nodeId)
else:
    cast = Network(nodeId)
print(f"nodeId: {nodeId}")
cast.myip = socket.gethostbyname(socket.gethostname())
print(f"myip: {cast.myip}")


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
    print(response)
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def newTransaction():
    values = request.json
    return _newTransaction(values)


@app.route('/transaction/sim/late', methods=['POST'])
def newTransactionLate():
    values = request.json
    values["order"] = 2  # 補助情報
    createTransaction(values)
    broadcast("transaction/new", values, 2)
    # del values["txid"]  # 新しいtxなのでtxidを削除
    values["order"] = 1  # 補助情報
    response = createTransaction(values)
    broadcast("transaction/new", values, -1)
    if hasattr(cast, "count"):
        cast.count[cast.myId] += 1
    else:
        print("no count")
    return jsonify(response), 201


@app.route('/transaction/sim/ds', methods=['POST'])
def doubleSpending():
    values = request.json

    sender = values.get("sender", nodeId)
    txid = values.get("txid", str(uuid4()).replace('-', ''))
    recipient = values['recipient']
    amount = values['amount']
    index = blockchain.newMaliciousTransaction(txid, sender, recipient, amount)

    # トランザクションをもう一つ作る
    txid = str(uuid4()).replace('-', '')
    index = blockchain.newTransaction(txid, sender, recipient, amount)
    if index is None:
        response = {'message': f'Transaction was already added'}
    else:
        print(f'Transaction will be added to Block {index}')
        response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


def _newTransaction(values):
    response, txid = createTransaction(values)
    values["txid"] = txid
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
        count = blockchain.pool.find().count()
        timestamp = time()
        print(f'[{timestamp}]Tx will be added to Block {index}, count: {count}')
        response = {
            'message': f'Transaction will be added to Block {index}',
            "timestamp": timestamp,
            "count": count
        }
    return response, txid


@app.route('/id', methods=['GET'])
def getId():
    return nodeId


@app.route('/chain/', methods=['GET'])
def fullChain():
    response = {
        'chain': list(blockchain.chain.find({}, {'_id': 0})),
        'length': blockchain.chain.count(),
    }
    return jsonify(response), 200


@app.route('/nodes/', methods=['GET'])
def getNodes():
    response = {
        "nodes": list(blockchain.nodes.find({}, {'_id': 0}))
    }
    return jsonify(response), 200


@app.route('/pool/', methods=['GET'])
def getPools():
    response = {
        "tx": list(blockchain.pool.find({}, {'_id': 0}))
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def registerNodes():
    values = request.json
    return cast.receive(values, _registerNode)


def _registerNode(values):
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400
    for node in nodes:
        if node == f"http://{cast.myip}":
            continue
        blockchain.registerNode(node)
    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes.find({}, {'_id': 0})),
    }
    print(f"myip: {cast.myip}")
    values["nodes"] = [f"http://{cast.myip}"]
    broadcast("nodes/register", values)
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET', 'POST'])
def consensus():
    replaced = blockchain.resolveConflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'newChain': list(blockchain.chain.find({}, {'_id': 0}))
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': list(blockchain.chain.find({}, {'_id': 0}))
        }
    return jsonify(response), 200


def broadcast(func, values, additional=1):
    cast.broadcast(func, values, list(
        blockchain.nodes.find({}, {'_id': 0})), additional)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    # cast.myip = f"http://127.0.0.1:{port}"
    app.run(host='0.0.0.0', port=port, debug=True)
