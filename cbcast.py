import hashlib
import json

import requests
from pymongo import MongoClient

mongoClient = MongoClient('localhost', 27017)
db = mongoClient.gc_blockchain


class CBCast(object):
    def __init__(self, myId):
        self.count = db.cbcast_count
        self.count.insert({"id": myId, "count": 0})
        self.myId = myId
        self.myip = ""
        self.vector_key = "cbcast_vector"
        self.sender_id = "sender_id"
        self.txqueue = db.cbcast_queue
        self.timeStampSync = False
        self.callback = None

    def objectHash(self, dic):
        return hashlib.md5(str(dic).encode('utf-8')).hexdigest()

    def broadcast(self, func, values, nodes, additional=1):
        nodeList = [x["url"] for x in nodes]
        received = set(values.get("received", []))
        received.add(self.myip)
        values["received"] = list(received)
        self.count.update({"id": self.myId}, {"$inc": {"count": additional}})
        print(f"received: {list(received)}")
        # print(f"countupdated: {self.count[self.myId]}")
        for node in set(nodeList) - received:
            self.send(f"http://{node}/{func}", values)

    def send(self, url, param={}):
        param[self.vector_key] = list(self.count.find({}, {'_id': 0}))
        param[self.sender_id] = self.myId
        print(f"sender: {param}")
        return requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})

    def receive(self, param, callback):
        sender_id = param.get(self.sender_id, None)
        if sender_id is None:
            return callback(param)
        if callback != "dummy":
            self.callback = callback
        #messageVector = param.get(self.vector_key, {})
        messageVector = {i["id"]: i["count"] for i in param.get(self.vector_key, [])}
        memoryVector = {i["id"]: i["count"] for i in list(self.count.find({}, {'_id': 0}))}
        ret = self.checkReceivable(memoryVector, messageVector, sender_id)
        # print(f"receivable: {ret}")
        if ret:
            self.updateMemoryVector(sender_id, messageVector)
            print(f"[ACCEPT] {messageVector[sender_id]}")
            tempQueue = self.txqueue.find({}, {'_id': 0})
            self.txqueue.remove()
            for q in tempQueue:
                self.receive(q["param"], q["callback"])
            return callback(param)
        else:
            # キューに貯めて受信可能になるのを待つ
            print(f"[REJECT] {messageVector[sender_id]}")
            self.txqueue.insert({"param": param, "callback": "dummy"})
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
        count = messageVector.get(senderId, 0)
        if self.count.find({"id": senderId}).count() > 0:
            self.count.update({"id": senderId}, {"id": senderId, "count": count})
        else:
            self.count.insert({"id": senderId, "count": count})
        # print(f"count updated: {self.count[senderId]}")
