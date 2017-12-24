import hashlib
import json

import requests


class CBCast(object):
    def __init__(self, myId):
        self.count = {myId: 0}
        self.myId = myId
        self.myip = ""
        self.vector_key = "cbcast_vector"
        self.sender_id = "sender_id"
        self.txqueue = []

    def objectHash(self, dic):
        return hashlib.md5(str(dic).encode('utf-8')).hexdigest()

    def broadcast(self, func, values, nodes, additional=1):
        received = set(values.get("received", []))
        received.add(self.myip)
        values["received"] = list(received)
        self.count[self.myId] += additional
        print(f"received: {list(received)}")
        # print(f"countupdated: {self.count[self.myId]}")
        for node in nodes - received:
            self.send(f"http://{node}/{func}", values)

    def send(self, url, param={}):
        param[self.vector_key] = self.count
        param[self.sender_id] = self.myId
        print(f"sender: {param}")
        return requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})

    def receive(self, param, callback):
        sender_id = param.get(self.sender_id, None)
        if sender_id is None:
            return callback(param)
        messageVector = param.get(self.vector_key, {})
        ret = self.checkReceivable(self.count, messageVector, sender_id)
        # print(f"receivable: {ret}")
        if ret:
            self.updateMemoryVector(sender_id, messageVector)
            print(f"[ACCEPT] {messageVector[sender_id]}")
            tempQueue = self.txqueue
            self.txqueue = []
            for q in tempQueue:
                self.receive(q["param"], q["callback"])
            return callback(param)
        else:
            # キューに貯めて受信可能になるのを待つ
            print(f"[REJECT] {messageVector[sender_id]}")
            self.txqueue.append({"param": param, "callback": callback})
            return callback(param)

    def checkReceivable(self, memoryVector, messageVector, senderId):
        vj = messageVector.get(senderId, 0)
        lj = memoryVector.get(senderId, 0)
        # print(f"vj: {vj}")
        # print(f"lj: {lj}")
        # print(f"vi: {messageVector.items()}")
        # print(f"li: {memoryVector.items()}")
        if lj + 1 != vj:
            return False
        for k, vi in messageVector.items():
            if k == senderId:
                continue
            if vi > memoryVector.get(k, 0):
                return False
        return True

    # 正しくメッセージが受信された時、正しく受信された最後の番号を入れる
    def updateMemoryVector(self, senderId, messageVector):
        self.count[senderId] = messageVector.get(senderId, 0)
        # print(f"count updated: {self.count[senderId]}")
