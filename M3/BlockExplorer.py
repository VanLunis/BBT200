'''
Linus Eriksson
Inlämning m3-uppgift-P1-explorer-python
BBT200
'''

import requests
import json
import os



RPC_USER = "admin"
RPC_PASSWORD = "admin"

URL = f"http://{RPC_USER}:{RPC_PASSWORD}@localhost:8332"
print(URL)
os.environ["NO_PROXY"] = URL
HEADERS = {"content-type": "application/json"}

payload = {
    "method": "getblockhash",
    "params": [99]
}

response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
print(response)

payload = {
    "method": "getblock",
    "params": ["00000000a11307821a7468c3a74fd694b5ffa64956bdd119494ce5933f8a72bb"]
}

response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
print(response)

payload = {
    "method": "getblockchaininfo"
}

response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
print(f"Blockchain size: {response['result']['blocks']} blocks")
