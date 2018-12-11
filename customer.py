import os

import Crypto
import Crypto.Random

from Crypto.PublicKey import RSA

import binascii


class Customer(object):
    def __init__(self, username):
        self.userName = username
        self.publicKey = ''
        self.privateKey = ''
        self.warehouse = os.path.join(os.path.join(os.getcwd(), 'users'), self.userName)
        os.makedirs(self.warehouse)
        self.new_wallet()

    def new_wallet(self):
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()

        self.privateKey = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        self.publicKey = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        with open(os.path.join(self.warehouse, 'privateKey'), 'w') as f:
            f.write(self.privateKey)

        with open(os.path.join(self.warehouse, 'publicKey'), 'w') as f:
            f.write(self.publicKey)
