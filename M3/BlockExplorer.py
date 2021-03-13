'''
Linus Eriksson
Inlämning m3-uppgift-P1-explorer-python
BBT200
'''

import datetime
import requests
import json

from progress.bar import Bar


RPC_USER = "admin"
RPC_PASSWORD = "admin"

URL = f"http://{RPC_USER}:{RPC_PASSWORD}@localhost:8332"
HEADERS = {"content-type": "application/json"}


class ScriptPubKey:
    def __init__(self, scp_in):
        self.asm = scp_in["asm"]
        self.hex = scp_in["hex"]
        self.type = scp_in["type"]
        self.isNull = self.type == "nulldata"
        if not self.isNull:
            self.reqSigs = scp_in["reqSigs"]
            self.address = scp_in["addresses"][0]


class Vin:
    def __init__(self, vin_in):
        self.sequence = vin_in["sequence"]
        self.coinbase = vin_in["coinbase"]


class VinTx:
    def __init__(self, vin_in):
        self.id = vin_in["txid"]
        self.vout = vin_in["vout"]
        self.scriptSig = vin_in["scriptSig"]
        self.sequence = vin_in["sequence"]
        self.witnesses = []
        for witness in vin_in["txinwitness"]:
            self.witnesses.append(witness)


class Vout:
    def __init__(self, vout_in, number):
        self.value = vout_in["value"]
        self.number = number
        self.n = vout_in["n"]
        self.scriptPubKey = ScriptPubKey(vout_in["scriptPubKey"])

    def __str__(self):
        retstr = f"Output {self.number}: "
        if self.scriptPubKey.isNull:
            retstr += "No address!"
        else:
            retstr += f"{self.value} to address: {self.scriptPubKey.address}"
        retstr += f" Type: {self.scriptPubKey.type}"
        return retstr


class Transaction:
    def __init__(self, response_result):
        try:
            self.id = response_result["txid"]
            self.transHash = response_result["hash"]
            self.version = response_result["version"]
            self.size = response_result["size"]
            self.vsize = response_result["vsize"]
            self.weight = response_result["weight"]
            self.locktime = response_result["locktime"]
            self.vin = []
            self.vout = []
            self.addressDict = {}
            self.blockhash = response_result["blockhash"]
            self.hex = response_result["hex"]
            self.confirmations = response_result["confirmations"]
            self.time = response_result["time"]
            self.blocktime = response_result["blocktime"]

            for vin in response_result["vin"]:
                if "txid" in vin.keys():
                    self.vin.append(VinTx(vin))
                else:
                    self.vin.append(Vin(vin))
            for number, vout in enumerate(response_result["vout"]):
                new_vout = Vout(vout, number)
                self.vout.append(new_vout)
                if not new_vout.scriptPubKey.isNull:
                    if new_vout.scriptPubKey.address in self.addressDict:
                        self.addressDict[new_vout.scriptPubKey.address].append(new_vout)
                    else:
                        self.addressDict[new_vout.scriptPubKey.address] = [new_vout]
        except KeyError as e:
            print(f"Error creating transaction, KeyError {e}")

    def __str__(self):
        retstr = f"Txid (hash): {self.transHash}\n" \
                 f"In block: {self.blockhash}\n" \
                 f"Inputs: {len(self.vin)}\n" \
                 f"Outputs: {len(self.vout)}\n"
        for output in (self.vout):
            retstr += f"   {str(output)}\n"
        return retstr

    def has_address(self, address: str):
        return address in self.addressDict.keys()

    def get_outputs_by_address(self, address: str):
        assert self.has_address(address), f"Error accessing address {address} in transaction {self.transHash}!"
        retstr = "      Outputs:\n"
        for output in self.addressDict[address]:
            retstr += f"         Output {output.number}: {output.value} BTE\n"
        return retstr

class Block:
    def __init__(self, response_result):
        try:
            self.blockhash = response_result["hash"]
            self.blocknumber = response_result["height"]
            self.confirmations = response_result["confirmations"]
            self.strippedsize = response_result["strippedsize"]
            self.size = response_result["size"]
            self.weight = response_result["weight"]
            self.version = response_result["version"]
            self.versionHex = response_result["versionHex"]
            self.merkleroot = response_result["merkleroot"]
            self.transactions = []
            self.addresDict = {}
            self.time = response_result["time"]
            self.mediantime = response_result["mediantime"]
            self.nonce = response_result["nonce"]
            self.bits = response_result["bits"]
            self.chainwork = response_result["chainwork"]
            self.numTransactions = response_result["nTx"]
            self.previousblockhash = response_result["previousblockhash"]

            if "nextblockhash" in response_result.keys():
                self.nextblockhash = response_result["nextblockhash"]
            else:
                self.nextblockhash = None

            for transaction in response_result["tx"]:
                new_trans = Transaction(_get_transaction(transaction))
                self.transactions.append(new_trans)
                for vout in new_trans.vout:
                    if not vout.scriptPubKey.isNull:
                        if vout.scriptPubKey.address in self.addresDict.keys():
                            self.addresDict[vout.scriptPubKey.address].append(new_trans)
                        self.addresDict[vout.scriptPubKey.address] = [new_trans]

            assert self.numTransactions == len(self.transactions), f"Block error detected," \
                                                                   f" num transactions {self.numTransactions}" \
                                                                   f" not equal to length of transaction list" \
                                                                   f" {len(self.transactions)}!"
        except KeyError as e:
            print(f"Error creating block, KeyError {e}")

    def __str__(self):
        retstr = f"Block hash: {self.blockhash}\n" \
                 f"Prev. hash: {self.previousblockhash}\n" \
                 f"Merkle root: {self.merkleroot}\n" \
                 f"Height: {self.blocknumber}\n" \
                 f"Time: {datetime.datetime.fromtimestamp(self.time).isoformat().replace('T', ' ')}\n" \
                 f"Transactions: {self.numTransactions}\n"
        for number, transaction in enumerate(self.transactions):
            retstr += f"   Transaction {number}: {transaction.transHash}\n"
        return retstr

    def has_address(self, address: str):
        return address in self.addresDict.keys()

    def get_transactions_from_address(self, address: str):
        assert self.has_address(address), f"Error accessing address {address} in block {self.blockhash}"
        retstr = f"In block {self.blocknumber}:\n"
        for transaction in self.addresDict[address]:
            retstr += f"   Tx: {transaction.transHash}\n"
            retstr += transaction.get_outputs_by_address(address)
        return retstr


def _get_block_by_hash(blockhash: str):
    payload = {
        "method": "getblock",
        "params": [blockhash]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    error = response["error"]
    if not error:
        result = response["result"]
    else:
        print(f"Error accessing block hash <{blockhash}>! Error: {error} with id {response['id']}")
        result = None
    return result


def _get_blockhash_by_number(blocknumber: int):
    payload = {
        "method": "getblockhash",
        "params": [blocknumber]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    error = response["error"]
    if not error:
        blockhash = response["result"]
    else:
        print(f"Error accessing block number <{blocknumber}>! Error: {error} with id {response['id']}")
        blockhash = None
    return blockhash


def _get_blockchain_info():
    payload = {
        "method": "getblockchaininfo"
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response


def _get_chain_info():
    payload = {
        "method": "getblockchaininfo"
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response


def _get_network_info():
    payload = {
        "method": "getnetworkinfo"
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response


def _get_mempool_info():
    payload = {
        "method": "getmempoolinfo"
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    return response


def _get_top_block(blockchain_info):
    return blockchain_info['result']['blocks']


def _get_transaction(transaction_hash: str):
    payload = {
        "method": "getrawtransaction",
        "params": [transaction_hash, True]
    }
    response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
    error = response["error"]
    if not error:
        transaction = response["result"]
    else:
        print(f"Error accessing transaction <{transaction_hash}>! Error: {error} with id {response['id']}")
        transaction = None
    return transaction


def _get_transaction_from_address(address: str, startblock: int, searchlength: int):
    endblock = startblock - searchlength
    print(f"Searching for addres {address} in blocks [{startblock}, {endblock}]")
    transaction_string = ""
    with Bar("Traversing blocks:", max=searchlength) as bar:
        for blocknumber in range(startblock, endblock - 1, -1):
            block = Block(_get_block_by_hash(_get_blockhash_by_number(blocknumber)))
            if block.has_address(address):
                transaction_string += block.get_transactions_from_address(address)
            bar.next()
    return transaction_string



myHash = _get_blockhash_by_number(3125)
blocket = _get_block_by_hash(myHash)
myBlock = Block(blocket)
myTrans = Transaction(_get_transaction("a29ad6390646bc495fb8d6b6571f1b75455b3914d6e3867631f7eee95097ed50"))

blockchain_info = _get_blockchain_info()
topBlock = _get_top_block(blockchain_info)
chaininfo = _get_chain_info()
mempoolinfo = _get_mempool_info()
networkinfo = _get_network_info()

print(str(myBlock))
print(str(myTrans))

transactions = myBlock.get_transactions_from_address("1eduGsrvBJcfyTMij2rYXk9viiVV78PNq")
print(transactions)

trans_string = _get_transaction_from_address("1eduGsrvBJcfyTMij2rYXk9viiVV78PNq", topBlock, 2000)
print(trans_string)