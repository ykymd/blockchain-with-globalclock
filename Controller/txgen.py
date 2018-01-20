import requests
import json
import sys
from time import sleep

args = sys.argv
# ノードに接続する
txAmount = int(args[1]) if len(args) > 2 else 100
freq = int(args[2]) if len(args) > 3 else 1  # 毎秒n回
param = {
  "recipient": "053263f820054c2c8b3cec23c40a73a3",
  "amount": 5
}
url = f"http://172.19.0.2/transaction/new"
print("try: ", url)
try:
    for i in range(txAmount):
        param["amount"] = i
        requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})
        print("success")
        sleep(1 / freq)
except Exception:
    print(sys.exc_info()[0])
