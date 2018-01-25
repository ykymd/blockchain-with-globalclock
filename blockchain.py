from time import time
import json
import hashlib
from urllib.parse import urlparse
import requests
import random
from pymongo import MongoClient

mongoClient = MongoClient('localhost', 27017)
db = mongoClient.gc_blockchain


class Blockchain(object):
    def __init__(self):
        self.chain = db.chain
        self.pool = db.pool
        self.nodes = db.node
        self.chain.remove()
        self.pool.remove()
        self.nodes.remove()
        # self.chain = []
        # self.txpool = []
        # self.nodes = set()
        # genesis blockを生成(全て固定値とする)
        self.newBlock(previousHash=1, proof=100, time=0)

    def newBlock(self, proof: int, previousHash: str = None, time: float = 0) -> dict:
        txpool = self.pool.find({}, {'_id': 0}).sort([("timestamp", 1)]) if self.pool.count() > 0 else {}
        txs = [t for t in txpool if self.validTx(t)]
        # 新しいブロックを生成して追加
        block = {
            'index': int(self.lastBlock['index']) + 1,
            'timestamp': time,
            'transactions': txs,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.lastBlock),
        }
        return self.addBlock(block)

    def addBlock(self, block):
        #leftTxids = set([x["txid"] for x in txpool]) - \
        #    set([x["txid"] for x in block['transactions']])
        for removeTxid in set([x["txid"] for x in block['transactions']]):
            self.pool.remove({"txid": removeTxid})
        #leftTx = []
        #for tx in txpool:
        #    if tx["txid"] in leftTxids:
        #        leftTx.append(tx)
        length = self.chain.find().count()
        if length > 0:
            lastBlock = self.lastBlock
            #print(f'{lastBlock}')
            #print(f'{block}')
            #print("\n---------\n")
            if block['previousHash'] != self.hash(lastBlock):
                return None
            if not self.validProof(lastBlock['proof'], block['proof']):
                return None
        #print(f"{self.chain.all()}")
        #print(f"add block{block['index']}")
        self.chain.insert(block)
        #print(f"document ID: {docId}")
        #print(f"{self.chain.all()}")
        return block

    def newTransaction(self, txid: str, sender: str, recipient: str, amount: int, time) -> int:
        """
        sender: 送り元のアドレス
        recipient: 送り先のアドレス
        return: blockのindex
        """
        # 重複しないかチェックする
        # txidList = [x["txid"] for x in self.txpool]
        txidList = self.pool.find({"txid": txid})
        # if txid in txidList:
        if txidList.count() > 0:
            return None
        else:
            self.pool.insert({
                'txid': txid,
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time
            })
            return self.lastBlock['index'] + 1

    def newMaliciousTransaction(self, txid: str, sender: str, recipient: str, amount: int, time) -> int:
        """
        sender: 送り元のアドレス
        recipient: 送り先のアドレス
        return: blockのindex
        """
        txidList = [x["txid"] for x in self.txpool.find({}, {'_id': 0})]
        if txid in txidList:
            return None
        else:
            # 意図的に無視されるトランザクション
            self.txpool.append({
                'txid': txid,
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time,
                'ignore': True
            })
            return self.lastBlock['index'] + 1

    def getBalance(self, nodeId):
        balance = 0
        for block in self.chain.find():
            for tx in block['transactions']:
                print(tx['recipient'])
                if tx['recipient'] == nodeId:
                    balance += int(tx['amount'])
                elif tx['sender'] == nodeId:
                    balance -= int(tx['amount'])
        return balance

    @staticmethod
    def hash(block: dict) -> str:
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        if self.chain.count() <= 0:
            return {'index': 0, 'proof': 100}
        return self.chain.find({}, {'_id': 0}).sort([('index', -1)]).limit(1)[0]

    def proofOfWork(self, lastProof: int) -> int:
        proof = random.randint(0, 1000000)
        while self.validProof(lastProof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validProof(lastProof: int, proof: int) -> bool:
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == "0000"

    def validTx(self, tx: dict) -> bool:
        required = ['txid', 'sender', 'recipient', 'amount']
        if not all(k in tx for k in required):
            print("INVALID: missing value")
            return False
        if not isinstance(tx['amount'], int):
            print("INVALID: type error")
            return False
        senderBalance = int(self.getBalance(tx['sender']))
        if senderBalance < int(tx['amount']) and tx['sender'] != '0':
            print("INVALID: insufficient funds")
            return False
        # シミュレーション用
        # 意図的に消したいトランザクションを除外する
        #if tx.get('ignore', False):
        #    print("INVALID: This is ignored transaction")
        #    return False
        return True

    def registerNode(self, address: str):
        if "http://" not in address:
            address = f"http://{address}"
        parsedUrl = urlparse(address)
        url = parsedUrl.netloc
        allnodes = [i["url"] for i in self.nodes.find()]
        if url not in allnodes:
            print(f"insert: {url}")
            self.nodes.insert({"url": url})

    def validChain(self, chain: list) -> bool:
        lastBlock = chain[0]
        currentIndex = 1

        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f'{lastBlock}')
            print(f'{block}')
            print("\n---------\n")
            if block['previousHash'] != self.hash(lastBlock):
                return False
            if not self.validProof(lastBlock['proof'], block['proof']):
                return False
            lastBlock = block
            currentIndex += 1
        return True

    def resolveConflicts(self) -> bool:
        bestChain = self.chain.find()
        maxLength = self.chain.count()
        replaced = False
        for node in self.nodes.find():
            url = node["url"]
            response = requests.get(f'http://{url}/chain')
            if response.status_code == 200:
                peerLength = response.json()['length']
                peerChain = response.json()['chain']
                peerChain = sorted(peerChain, key=lambda x: x['index'])
                if not self.validChain(peerChain):
                    print("no valid chain")
                    continue
                # 最も長いチェーンを最良のチェーンとする
                if peerLength > maxLength:
                    print("their chain is better")
                    maxLength = peerLength
                    bestChain = peerChain
                    replaced = True
                # 長さが同じ場合それぞれのチェーンを比べる
                elif peerLength == maxLength and self.validBetterChain(peerChain, bestChain):
                    print("their chain is better: same length")
                    bestChain = peerChain
                    replaced = True
        if replaced:
            #self.db.purge_table("chain")
            #self.chain = self.db.table("chain")
            #self.chain.insert_multiple(bestChain)
            for block in bestChain:
                if self.chain.find({"index": block['index']}).count() > 0:
                    self.chain.update({"index": block['index']}, block)
                else:
                    self.chain.insert(block)
        #print(f"updated chain: {self.chain.all()}")
        return replaced

    @staticmethod
    def validBetterChain(target: list, comparison: list) -> bool:
        # proofの合計値が少ない方が最良のチェーンとする（できれば確率の低い方にしたい）
        proofSumT = sum(list(map(lambda a: a["proof"], target)))
        proofSumC = sum(list(map(lambda a: a["proof"], comparison)))
        print(f'target: {proofSumT}')
        print(f'comparison: {proofSumC}')
        return proofSumT < proofSumC
