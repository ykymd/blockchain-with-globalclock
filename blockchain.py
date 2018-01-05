from time import time
import json
import hashlib
from urllib.parse import urlparse
import requests
import random


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.txpool = []
        self.nodes = set()
        # genesis blockを生成(全て固定値とする)
        self.newBlock(previousHash=1, proof=100, time=0)

    def newBlock(self, proof: int, previousHash: str = None, time: float = time()) -> dict:
        self.txpool.sort(key=lambda x: x["timestamp"])
        txs = [t for t in self.txpool if self.validTx(t)]
        # 新しいブロックを生成して追加
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time,
            'transactions': txs,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1]),
        }
        return self.addBlock(block)

    def addBlock(self, block):
        leftTxids = set([x["txid"] for x in self.txpool]) - \
            set([x["txid"] for x in block['transactions']])
        leftTx = []
        for tx in self.txpool:
            if tx["txid"] in leftTxids:
                leftTx.append(tx)
        self.txpool = leftTx
        self.chain.append(block)
        return block

    def newTransaction(self, txid: str, sender: str, recipient: str, amount: int) -> int:
        """
        sender: 送り元のアドレス
        recipient: 送り先のアドレス
        return: blockのindex
        """
        # 重複しないかチェックする
        txidList = [x["txid"] for x in self.txpool]
        if txid in txidList:
            return None
        else:
            self.txpool.append({
                'txid': txid,
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time()
            })
            return self.lastBlock['index'] + 1

    def newMaliciousTransaction(self, txid: str, sender: str, recipient: str, amount: int) -> int:
        """
        sender: 送り元のアドレス
        recipient: 送り先のアドレス
        return: blockのindex
        """
        txidList = [x["txid"] for x in self.txpool]
        if txid in txidList:
            return None
        else:
            # 意図的に無視されるトランザクション
            self.txpool.append({
                'txid': txid,
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'timestamp': time(),
                'ignore': True
            })
            return self.lastBlock['index'] + 1

    def getBalance(self, nodeId):
        balance = 0
        for block in self.chain:
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
        return self.chain[-1]

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
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

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
        bestChain = self.chain
        maxLength = len(self.chain)
        replaced = False
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                peerLength = response.json()['length']
                peerChain = response.json()['chain']
                if not self.validChain(peerChain):
                    continue
                # 最も長いチェーンを最良のチェーンとする
                if peerLength > maxLength:
                    maxLength = peerLength
                    bestChain = peerChain
                    replaced = True
                # 長さが同じ場合それぞれのチェーンを比べる
                elif peerLength == maxLength and self.validBetterChain(peerChain, bestChain):
                    bestChain = peerChain
                    replaced = True
        self.chain = bestChain
        return replaced

    @staticmethod
    def validBetterChain(target: list, comparison: list) -> bool:
        # proofの合計値が少ない方が最良のチェーンとする（できれば確率の低い方にしたい）
        # TODO: グローバルクロック化
        proofSumT = sum(list(map(lambda a: a["proof"], target)))
        proofSumC = sum(list(map(lambda a: a["proof"], comparison)))
        print(f'target: {proofSumT}')
        print(f'comparison: {proofSumC}')
        return proofSumT < proofSumC
