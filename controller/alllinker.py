import requests
import json
import sys
from time import sleep

args = sys.argv
# ノードに接続する
nodeCount = int(args[1]) if len(args) > 2 else 1

for regId in range(2, nodeCount+2):
    for targetId in range(regId+1, nodeCount+2):
        param = {
            "nodes": [f"http://172.19.0.{regId}"]
        }
        url = f"http://172.19.0.{targetId}/nodes/register"
        print("try: ", url)
        try:
            requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})
            print("success")
        except Exception:
            print(sys.exc_info()[0])
        sleep(1)
