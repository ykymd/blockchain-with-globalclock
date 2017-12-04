from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
import requests
import json

app = Flask(__name__)
nodeId = str(uuid4()).replace('-', '')
blockchain = Blockchain()
myip = ""


@app.route('/mine', methods=['GET'])
def mine():
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)
    reward = 100

    blockchain.newTransaction(
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
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def newTransaction():
    values = request.json

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


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
    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply a valid list of nodes', 400
    for node in nodes:
        duplicate = blockchain.registerNode(node)
        if not duplicate and values.get('recursive', False):
            requests.post(f"{node}/nodes/register", data=json.dumps({"nodes": [myip], "recursive": False}), headers={"content-type": "application/json"})
    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes),
    }
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


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    # socket.gethostbyname(socket.gethostname())
    myip = f"http://127.0.0.1:{port}"
    app.run(host='0.0.0.0', port=port)
