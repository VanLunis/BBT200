import datetime
import requests
import json

from PrivateKey import CoinKey, ElipsisPoint

RPC_USER = "admin"
RPC_PASSWORD = "admin"

URL = f"http://{RPC_USER}:{RPC_PASSWORD}@localhost:8332"
HEADERS = {"content-type": "application/json"}


def _create_raw_transaction(transaction_id, output_number, address, amount):
    inputs = {
        "txid": transaction_id,
        "vout": output_number,
    }
    outputs = {
        address: str(amount)
    }
    payload = {
        "method": "createrawtransaction",
        "params": [[inputs], [outputs]]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response["result"]


def _sign_raw_transaction(transaction_hex, private_keys):
    payload = {
        "method": "signrawtransactionwithkey",
        "params": [transaction_hex, private_keys]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response["result"]


def _send_raw_transaction(signed_hex, allow_high_fees=False):
    payload = {
        "method": "sendrawtransaction",
        "params": [signed_hex, allow_high_fees]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response["result"]


def main():
    raw = _create_raw_transaction("e2d1bf5083155814cdba69773a4d15c7619e0abaa77974fc797e8e817b0ab849", 1, "17L9gukeJ2ViUhntFFeCz5rN7QBaB6mr2d", 0.1)
    signed = _sign_raw_transaction(raw, ["Ky61jh5ieJSkcyhtT533fsT9FZovZXiVvAeaYZUFLHc38kRgNUSc"])
    sent = _send_raw_transaction(signed["hex"])
    return True


if __name__ == '__main__':
    main()
    exit(0)