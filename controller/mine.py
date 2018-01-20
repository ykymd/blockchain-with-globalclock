import requests
import sys
from time import sleep

i = 0
try:
    while(True):
        i += 1
        url = f"http://myblockchain_miner_{i}/mine"
        res = requests.get(url)
        print(res.status)
        sleep(1)
except Exception:
    print(sys.exc_info()[0])
