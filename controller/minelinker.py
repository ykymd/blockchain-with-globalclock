import requests
import sys
from time import sleep
import json

args = sys.argv

miner_url = args[1] if len(args) > 1 else "http://myblockchain_miner_1"
i = 0
try:
    while(True):
        i += 1
        param = {
            "nodes": [f"http://myblockchain_bc_{i}"]
        }
        url = f"{miner_url}/nodes/register"
        res = requests.post(url, data=json.dumps(param), headers={"content-type": "application/json"})
        print(res.status)
        sleep(1)
except Exception:
    print(sys.exc_info()[0])
