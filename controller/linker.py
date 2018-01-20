import requests
import json
import sys

args = sys.argv
# ノードに接続する
regId = args[1] if len(args) > 1 else "http://172.19.0.2"
targetId = args[2] if len(args) > 2 else "http://172.19.0.3"
param = {
    "nodes": [regId]
}
url = f"{targetId}/nodes/register"
print("try: ", url)
try:
    requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})
    print("success")
except Exception:
    print(sys.exc_info()[0])
