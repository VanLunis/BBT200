import requests
import json

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
    error = response["error"]
    if not error:
        return response["result"]
    else:
        print(f"Error creating transaction! Code: {error['code']} with message {error['message']}")
        return None


def _sign_raw_transaction(transaction_hex, private_keys):
    payload = {
        "method": "signrawtransactionwithkey",
        "params": [transaction_hex, private_keys]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    error = response["error"]
    if not error:
        return response["result"]
    else:
        print(f"Error signing transaction! Code: {error['code']} with message {error['message']}")
        return None


def _send_raw_transaction(signed_hex, allow_high_fees=0):
    payload = {
        "method": "sendrawtransaction",
        "params": [signed_hex, allow_high_fees]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    error = response["error"]
    if not error:
        return response["result"]
    else:
        print(f"Error sending transaction! Code: {error['code']} with message {error['message']}")
        return None


def _system_loop():
    while True:
        print("Enter hash id for transaction to spend:")
        transid = input()
        print("Enter output number for input to spend:")
        vout_number = int(input())
        print("Enter address to send to:")
        address = input()
        print("Enter amount to send (BTE):")
        amount = float(input())
        print("Enter private key for signing:")
        key = input()
        print(f"About to send {amount} BTE from vout {vout_number} of transaction "
              f"{transid} to {address} and sign with {key}\n"
              f"Continue? y/n")
        choice = input()
        if choice.lower() == "y":
            raw = _create_raw_transaction(transid,vout_number, address, amount)
            if raw:
                signed = _sign_raw_transaction(raw, [key])
                if signed:
                    sent = _send_raw_transaction(signed["hex"])
                    if sent:
                        print(sent)


def main():
    _system_loop()


if __name__ == '__main__':
    main()
    exit(0)
