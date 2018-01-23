import hashlib
import json

import requests
from pymongo import MongoClient

mongoClient = MongoClient('localhost', 27017)
db = mongoClient.gc_blockchain


class Vector(object):
    def __init__(self, myId):
        self.count = db.cbcast_count
        self.count.insert({"id": myId, "count": 0})
        self.myId = myId
        self.myip = ""
        self.vector_key = "cbcast_vector"
        self.sender_id = "sender_id"
        self.timeStampSync = False
        self.callback = None

    def objectHash(self, dic):
        return hashlib.md5(str(dic).encode('utf-8')).hexdigest()

    def broadcast(self, func, values, nodes, additional=1):
        nodeList = [x["url"] for x in nodes]
        received = set(values.get("received", []))
        received.add(self.myip)
        values["received"] = list(received)
        print(f"received: {list(received)}")
        # print(f"countupdated: {self.count[self.myId]}")
        for node in set(nodeList) - received:
            print(f"try: http://{node}/{func}")
            self.send(f"http://{node}/{func}", values)
        # 全て送信完了後に可算する
        self.count.update({"id": self.myId}, {"$inc": {"count": additional}})

    def send(self, url, param={}):
        param[self.vector_key] = list(self.count.find({}, {'_id': 0}))
        param[self.sender_id] = self.myId
        print(f"sender: {param}")
        return requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})

    def receive(self, param, callback):
        sender_id = param.get(self.sender_id, None)
        if sender_id is None:
            print("sender_id is None")
            return callback(param)
        messageVector = {i["id"]: i["count"] for i in param.get(self.vector_key, [])}
        memoryVector = {i["id"]: i["count"] for i in list(self.count.find({}, {'_id': 0}))}
        self.updateMemoryVector(memoryVector, messageVector, sender_id)
        print(f"[Received] {messageVector[sender_id]}")
        return callback(param)

    def updateMemoryVector(self, memoryVector, messageVector, senderId):
        for k, v in messageVector.items():
            if v > memoryVector.get(k, 0):
                memoryVector[k] = v
                if self.count.find({"id": k}).count() > 0:
                    self.count.update({"id": k}, {"id": k, "count": v})
                else:
                    self.count.insert({"id": k, "count": v})
