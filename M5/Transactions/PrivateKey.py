"""
Linus Eriksson
m5-uppgift-P2-wallet-tx-python
BBT200
"""

import binascii
import hashlib
import secrets
import random

from pycoin.ecdsa.secp256k1 import secp256k1_generator as secpGen
from pycoin.ecdsa.secp256k1 import _r
from pycoin.encoding import b58
from pycoin.contrib import segwit_addr

GENERATOR = secpGen


class ElipsisPoint:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def _get_sec(self, value):
        return "%064x" % value

    def get_sec_x(self):
        return self._get_sec(self.x)

    def get_sec_y(self):
        return self._get_sec(self.y)

    def get_uncompressed(self):
        x = self.get_sec_x()
        y = self.get_sec_y()
        uncompressed = "04" + x + y
        return uncompressed

    def get_compressed(self):
        if self.y % 2 == 0:
            prefix = "02"
        else:
            prefix = "03"
        compressed = prefix + self.get_sec_x()
        return compressed


class CoinKey:

    def __init__(self):
        self.private_key = None
        self.private_hex = None
        self.public_key_point = None
        self.uncompressed = None
        self.compressed = None
        self.uncom_hash160 = None
        self.com_hash160 = None
        self.uncom_bitcoin = None
        self.com_bitcoin = None
        self.uncom_wif = None
        self.com_wif = None
        self.segwit_p2sh = None
        self.segwit_p2wpkh = None

    # Double sha256 function, taken from https://colab.research.google.com/drive/1Eb4bNE8HU9sULhEqEXCWwuQ9UkG-xsm4
    @classmethod
    def _double_sha256(cls, value):
        return hashlib.sha256(hashlib.sha256(binascii.unhexlify(value)).digest()).hexdigest()

    # Hash160 function, taken from https://colab.research.google.com/drive/1Eb4bNE8HU9sULhEqEXCWwuQ9UkG-xsm4
    @classmethod
    def _hash160(cls, value):
        return hashlib.new('ripemd160', hashlib.sha256(binascii.unhexlify(value)).digest()).hexdigest()

    @classmethod
    def _create_base58_with_checksum(cls, data):
        checksum = CoinKey._double_sha256(data)[:8]
        return_data = data + checksum
        return_data = b58.b2a_base58(binascii.unhexlify(return_data))
        return return_data

    def generate_private_safe(self):
        cryptsafe_gen = secrets.SystemRandom()
        self.private_key = cryptsafe_gen.randrange(0, _r)

    def set_private(self, value):
        if value < _r:
            self.private_key = value
        else:
            raise ValueError(f"Private key {value} larger than max {_r}!")

    def get_private_hex(self):
        if self.private_hex is None:
            self.private_hex = hex(self.private_key)
        return self.private_hex

    def generate_private_with_seed(self, seed):
        random.seed(seed)
        self.private_key = random.randrange(0, _r)

    def generate_public_key(self, generator: secpGen = GENERATOR, regenerate=False):
        if self.public_key_point is None or regenerate:
            if self.private_key is None:
                raise ValueError("Can not generate public key without private key!")
            (x, y) = self.private_key * generator
            self.public_key_point = ElipsisPoint(x, y)

    def get_uncompressed(self):
        if self.uncompressed is None:
            if self.public_key_point is None:
                raise ValueError("Public key not generated!")
            self.uncompressed = self.public_key_point.get_uncompressed()
        return self.uncompressed

    def get_compressed(self):
        if self.compressed is None:
            if self.public_key_point is None:
                raise ValueError("Public key not generated!")
            self.compressed = self.public_key_point.get_compressed()
        return self.compressed

    def get_uncompressed_hash160_address(self):
        if self.uncom_hash160 is None:
            self.uncom_hash160 = CoinKey._hash160(self.get_uncompressed())
        return self.uncom_hash160

    def get_compressed_hash160_address(self):
        if self.com_hash160 is None:
            self.com_hash160 = CoinKey._hash160(self.get_compressed())
        return self.com_hash160

    def get_uncompressed_bitcoin_address(self, prefix: str):
        if self.uncom_bitcoin is None:
            data = prefix + self.get_uncompressed_hash160_address()
            self.uncom_bitcoin = CoinKey._create_base58_with_checksum(data)
        return self.uncom_bitcoin

    def get_compressed_bitcoin_address(self, prefix: str):
        if self.com_bitcoin is None:
            data = prefix + self.get_compressed_hash160_address()
            self.com_bitcoin = CoinKey._create_base58_with_checksum(data)
        return self.com_bitcoin

    def get_compressed_wif_format(self):
        if self.private_key is None:
            raise ValueError("Can not get WIF format without private key!")
        if self.com_wif is None:
            hex_key = "%064x" % self.private_key
            suffix = "01"
            data = "80" + hex_key + suffix
            self.com_wif = CoinKey._create_base58_with_checksum(data)
        return self.com_wif

    def get_uncompressed_wif_format(self):
        if self.private_key is None:
            raise ValueError("Can not get WIF format without private key!")
        if self.uncom_wif is None:
            hex_key = "%064x" % self.private_key
            data = "80" + hex_key
            self.uncom_wif = CoinKey._create_base58_with_checksum(data)
        return self.uncom_wif

    def get_p2sh_segwit(self):
        if self.segwit_p2sh is None:
            compressed = self.get_compressed_hash160_address()
            with_signature = "0014" + compressed
            hashed_signature = CoinKey._hash160(with_signature)
            data = "05" + hashed_signature
            self.segwit_p2sh = CoinKey._create_base58_with_checksum(data)
        return self.segwit_p2sh

    def get_p2wpkh_segwit(self, witness_version: int):
        if self.segwit_p2wpkh is None:
            compressed = self.get_compressed_hash160_address()
            prefix = "bc"
            self.segwit_p2wpkh = segwit_addr.encode(prefix, witness_version, binascii.unhexlify(compressed))
        return self.segwit_p2wpkh

    def __str__(self):
        if self.public_key_point is None:
            raise ValueError("No public key generated!")
        retstr = f"Private key: {self.private_key}\n" \
                 f"Private key hex: {self.get_private_hex()}\n" \
                 f"Public key point: x: {self.public_key_point.x} y: {self.public_key_point.y}\n" \
                 f"Uncompressed public key: {self.get_uncompressed()}\n" \
                 f"Compressed public key: {self.get_compressed()}\n" \
                 f"Uncompressed Hash160 address: {self.get_uncompressed_hash160_address()}\n" \
                 f"Compressed Hash160 address: {self.get_compressed_hash160_address()}\n" \
                 f"Uncompressed Bitcoin address: {self.get_uncompressed_bitcoin_address('00')}\n" \
                 f"Compressed Bitcoin address: {self.get_compressed_bitcoin_address('00')}\n" \
                 f"Uncompressed wif: {self.get_uncompressed_wif_format()}\n" \
                 f"Compressed wif: {self.get_compressed_wif_format()}\n" \
                 f"Segwit P2SH: {self.get_p2sh_segwit()}\n" \
                 f"Segwit P2WPKH: {self.get_p2wpkh_segwit(0)}"
        return retstr
