import hashlib
import json

import requests


class Network(object):
    def __init__(self, myId):
        self.myId = myId
        self.myip = ""
        self.timeStampSync = True

    def objectHash(self, dic):
        return hashlib.md5(str(dic).encode('utf-8')).hexdigest()

    def broadcast(self, func, values, nodes, additional=1):
        received = set(values.get("received", []))
        received.add(self.myip)
        values["received"] = list(received)
        print(f"received: {list(received)}")
        nodeset = set([i["url"] for i in nodes])
        # print(f"countupdated: {self.count[self.myId]}")
        for node in nodeset - received:
            self.send(f"http://{node}/{func}", values)

    def send(self, url, param={}):
        print(f"sender: {param}")
        return requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})

    def receive(self, param, callback):
        return callback(param)
