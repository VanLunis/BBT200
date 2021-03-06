"""
Linus Eriksson
Inlämning m3-uppgift-P1-explorer-python
BBT200
"""

import datetime
import requests
import json

from progress.bar import Bar


RPC_USER = "admin"
RPC_PASSWORD = "admin"

URL = f"http://{RPC_USER}:{RPC_PASSWORD}@localhost:8332"
HEADERS = {"content-type": "application/json"}


ACTION_CHOICES = {
    1: "Show block by number",
    2: "Show block by hash",
    3: "Show transaction by hash",
    4: "Show outputs for address",
    5: "Reload data",
    0: "Exit program"
}


class Networkinfo():
    def __init__(self):
        self.update()

    def update(self):
        result = self._get_network_info()
        self._set_values(result)

    def _set_values(self, response_result):
        self.version = response_result["version"]
        self.subversion = response_result["subversion"]
        self.protocolversion = response_result["protocolversion"]
        self.localservices = response_result["localservices"]
        self.localservicesnames = response_result["localservicesnames"]
        self.localrelay = response_result["localrelay"]
        self.timeoffset = response_result["timeoffset"]
        self.networkactive = response_result["networkactive"]
        self.connections = response_result["connections"]
        self.connections_in = response_result["connections_in"]
        self.connections_out = response_result["connections_out"]
        self.networks = response_result["networks"]
        self.relayfee = response_result["relayfee"]
        self.incrementalfee = response_result["incrementalfee"]
        self.localaddresses = response_result["localaddresses"]
        self.warnings = response_result["warnings"]

    def _get_network_info(self):
        payload = {
            "method": "getnetworkinfo"
        }
        response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
        return response["result"]


class Mempoolinfo:
    def __init__(self):
        self.update()

    def update(self):
        result = self._get_mempool_info()
        self._set_values(result)

    def _set_values(self, response_result):
        self.loaded = response_result["loaded"]
        self.size = response_result["size"]
        self.bytes = response_result["bytes"]
        self.usage = response_result["usage"]
        self.maxmempool = response_result["maxmempool"]
        self.mempoolminfee = response_result["mempoolminfee"]
        self.minrelaytxfee = response_result["minrelaytxfee"]
        self.unbroadcastcount = response_result["unbroadcastcount"]

    def _get_mempool_info(self):
        payload = {
            "method": "getmempoolinfo"
        }
        response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
        return response["result"]


class BlockchainInfo:
    def __init__(self):
        self.update()

    def update(self):
        result = self._get_blockchain_info()
        self._set_blockchain_values(result)
        self.mempool = Mempoolinfo()
        self.network = Networkinfo()

    def _set_blockchain_values(self, response_result):
        self.chain = response_result["chain"]
        self.blocks = response_result["blocks"]
        self.headers = response_result["headers"]
        self.bestblockhash = response_result["bestblockhash"]
        self.difficulty = response_result["difficulty"]
        self.mediantime = response_result["mediantime"]
        self.verificationprogress = response_result["verificationprogress"]
        self.initialblockdownload = response_result["initialblockdownload"]
        self.chainwork = response_result["chainwork"]
        self.size_on_disk = response_result["size_on_disk"]
        self.pruned = response_result["pruned"]
        self.softforks = response_result["softforks"]
        self.warnings = response_result["warnings"]

    def __str__(self):
        retstr = f"Number of blocks: {self.blocks}\n" \
                 f"Size on disk: {self.size_on_disk / 1000000} MB\n" \
                 f"Latest block: {self.bestblockhash}\n" \
                 f"Mempool size (transactions): {self.mempool.size}\n" \
                 f"Connections: {self.network.connections}"
        return retstr

    def _get_blockchain_info(self):
        payload = {
            "method": "getblockchaininfo"
        }
        response = requests.post(URL, data=json.dumps(payload), headers=HEADERS).json()
        return response["result"]


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
            retstr += f"{self.value:06f} BTE to address: {self.scriptPubKey.address}"
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
        retstr = f"Txid (hash): {self.id}\n" \
                 f"In block: {self.blockhash}\n" \
                 f"Inputs: {len(self.vin)}\n" \
                 f"Outputs: {len(self.vout)}\n"
        for output in (self.vout):
            retstr += f"   {str(output)}\n"
        return retstr[:-1]

    def has_address(self, address: str):
        return address in self.addressDict.keys()

    def get_outputs_by_address(self, address: str):
        assert self.has_address(address), f"Error accessing address {address} in transaction {self.transHash}!"
        retstr = "      Outputs:\n"
        for output in self.addressDict[address]:
            retstr += f"         Output {output.number}: {output.value:6f} BTE\n"
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
            self.difficulty = response_result["difficulty"]
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
                 f"Difficulty: {self.difficulty}\n" \
                 f"Transactions: {self.numTransactions}\n"
        for number, transaction in enumerate(self.transactions):
            retstr += f"   Transaction {number}: {transaction.id}\n"
        return retstr[:-1]

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
    print(f"Searching for addres {address} in blocks [{startblock} -> {endblock}]")
    transaction_string = ""
    with Bar("Traversing blocks:", max=searchlength) as bar:
        for blocknumber in range(startblock, endblock - 1, -1):
            block = Block(_get_block_by_hash(_get_blockhash_by_number(blocknumber)))
            if block.has_address(address):
                transaction_string += block.get_transactions_from_address(address)
            bar.next()
    if transaction_string == "":
        transaction_string = f"No transactions found between blocks {endblock} and {startblock} for address <{address}>!\n"
    return transaction_string[:-1]


def _get_blockobject_by_hash(blockhas: str):
    return Block(_get_block_by_hash(blockhas))


def _get_blockobject_by_number(blocknumber: int):
    return _get_blockobject_by_hash(_get_blockhash_by_number(blocknumber))


def _get_transaction_object_by_hash(transhash: str):
    return Transaction(_get_transaction(transhash))


def get_transactions_from_address(blockchaininfo):
    print("Input address:")
    address = input()
    print("*" * 64)
    print(_get_transaction_from_address(address, blockchaininfo.blocks, 2000))
    return True


def get_blockinfo_by_number(blockchaininfo = None):
    print("Input blocknumber:")
    blocknumber = input()
    while not blocknumber.isnumeric():
        print("Input valid integer blocknumber!")
        blocknumber = input()
    print("*" * 64)
    block = _get_blockobject_by_number(int(blocknumber))
    print(str(block))
    return True


def get_blockinfo_by_hash(blockchaininfo = None):
    print("Input blockhash:")
    blockhash = input()
    print("*" * 64)
    print(str(_get_blockobject_by_hash(blockhash)))
    return True


def get_transaction_by_hash(blockchaininfo = None):
    print("Input transaction hash:")
    transhash = input()
    print("*" * 64)
    print(str(_get_transaction_object_by_hash(transhash)))
    return True


def _print_blockchain_info(blockchaininfo: BlockchainInfo):
    print("*" * 64)
    print(str(blockchaininfo))


def reload_data(blockchaininfo: BlockchainInfo):
    blockchaininfo.update()
    _print_blockchain_info(blockchaininfo)
    return True


def end_program(blockchaininfo = None):
    print("Exiting, thank you for using and have a great day!")
    return False


def _print_action_info():
    print("Select action:")
    for number, action in ACTION_CHOICES.items():
        print(f"{number}. {action}")


def _system_loop():
    actions = {
        1: get_blockinfo_by_number,
        2: get_blockinfo_by_hash,
        3: get_transaction_by_hash,
        4: get_transactions_from_address,
        5: reload_data,
        0: end_program
    }
    blockchaininfo = BlockchainInfo()
    _print_blockchain_info(blockchaininfo)
    print("*" * 64)
    while True:
        _print_action_info()
        selection = input()
        keep_going = True
        try:
            keep_going = actions[int(selection)](blockchaininfo)
        except KeyError:
            print(f"No action mapped for selection {selection}")
        except ValueError:
            print("Input integer for selection")
        if not keep_going:
            break
        print("*" * 64 + "\n")


def main():
    _system_loop()
    exit(0)


if __name__ == '__main__':
    main()
