import binascii
import hashlib
import math
import secrets
import random

from pycoin.ecdsa.secp256k1 import secp256k1_generator as secpGen
from pycoin.ecdsa.secp256k1 import _r
from pycoin.encoding import b58

GENERATOR = secpGen

class ElipsisPoint:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def _get_sec(self, value):
        return "%064x%" % value

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
    private_key: int
    name: str
    public_key_point: ElipsisPoint
    uncompressed: int
    compressed: int

    def __init__(self, name):
        self.name = name

    # Double sha256 function, taken from https://colab.research.google.com/drive/1Eb4bNE8HU9sULhEqEXCWwuQ9UkG-xsm4
    @classmethod
    def _double_sha256(cls, value):
        return hashlib.sha256(hashlib.sha256(binascii.unhexlify(value)).digest()).hexdigest()

    # Hash160 function, taken from https://colab.research.google.com/drive/1Eb4bNE8HU9sULhEqEXCWwuQ9UkG-xsm4
    @classmethod
    def _hash160(cls, value):
        return hashlib.new('ripemd160', hashlib.sha256(binascii.unhexlify(value)).digest()).hexdigest()

    @classmethod
    def _create_bitcoin_address(cls, data):
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

    def generate_private_with_seed(self, seed):
        random.seed(seed)
        self.private_key = random.randrange(0, _r)

    def generate_public_key(self, generator: secpGen):
        if self.private_key is None:
            raise ValueError("Can not generate public key without private key!")
        (x, y) = self.private_key * generator
        self.public_key_point = ElipsisPoint(x, y)

    def get_uncompressed(self):
        if self.public_key_point is None:
            raise ValueError("Public key not generated!")
        return self.public_key_point.get_uncompressed()

    def get_compressed(self):
        if self.public_key_point is None:
            raise ValueError("Public key not generated!")
        return self.public_key_point.get_compressed()

    def get_uncompressed_hash160_address(self):
        hashed = CoinKey._hash160(self.get_uncompressed())
        return hashed

    def get_compressed_hash160_address(self):
        hashed = CoinKey._hash160(self.get_compressed())
        return hashed

    def get_uncompressed_bitcoin_address(self, prefix: str):
        data = prefix + self.get_uncompressed_hash160_address()
        address = CoinKey._create_bitcoin_address(data)
        return address

    def get_compressed_bitcoin_address(self, prefix: str):
        data = prefix + self.get_compressed_hash160_address()
        address = CoinKey._create_bitcoin_address(data)
        return address
