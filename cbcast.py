import json
from urllib.parse import urlparse

import requests


class CBCast(object):
    def __init__(self, myId):
        self.count = {myId: 0}
        self.myId = myId
        self.myip = ""
        self.vector_key = "cbcast_vector"
        self.sender_id = "sender_id"

    def broadcast(self, func, values, nodes):
        received = set(values.get("received", []))
        received.add(urlparse(self.myip).netloc)
        values["received"] = list(received)
        self.count[self.myId] += 1
        for node in nodes - received:
            self.send(f"http://{node}/{func}", values)

    def send(self, url, param={}):
        param[self.vector_key] = self.count
        param[self.sender_id] = self.myId
        print(f"sender: {param}")
        return requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})

    def receive(self, param, callback):
        if param.get(self.sender_id, None) is None:
            return callback(param)
        messageVector = param.get(self.vector_key, {})
        ret = self.checkReceivable(
            self.count, messageVector, param.get(self.sender_id, ""))
        print(f"receivable: {ret}")
        if ret:
            self.updateMemoryVector(param.get(self.sender_id, ""), messageVector)
            print(self.count)
            return callback(param)
        return callback(param)

    def checkReceivable(self, memoryVector, messageVector, senderId):
        vj = messageVector.get(senderId, 0)
        print(f"vj: {vj}")
        print(f"li: {memoryVector.values()}")
        print(f"vi: {messageVector.items()}")
        for li in memoryVector.values():
            if li + 1 != vj:
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
