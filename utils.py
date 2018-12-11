import os
import shutil
import pickle
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii
import matplotlib.pyplot as plt
import random
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from collections import OrderedDict
import json


class Shop(object):
    def __init__(self):
        self.chain = []  # BlockChain the shop hold
        if os.path.exists('userlist.pkl'):
            with open('userlist.pkl', 'rb') as f:  #load
                print('Load user list from local file userlist.pkl' )
                self.userList = pickle.load(f)
        else:
            self.userList = {}  # Customer list
        self.currentUser = None
        self.work_directory = os.getcwd()
        if not os.path.exists('shelf'):
            os.makedirs('shelf')
        self.shelf_dir = os.path.join(self.work_directory, 'shelf')
        if os.path.exists('shelf_list.pkl'):
            with open('shelf_list.pkl', 'rb') as f:  #load
                print('Load user list from local file shelf_list.pkl' )
                self.shelf_list = pickle.load(f)
        else:
            self.shelf_list = {}  # Customer list

    def register(self, username=None):  # Sign up with unique user name
        if not isinstance(username, str):
            print('It is not string')
            username = str(username)  # Check username's data type
        if username in self.userList.keys():  # Check if username exist
            print('User name is exist, please try another user name')
            return None
        else:
            new_user = Customer(username)  # Return a new customer instance
            self.userList['%s' % new_user.userName] = {
                'publicKey': new_user.publicKey,
                'warehouse': new_user.warehouse,
                'pets': {},
            }
            # self.award(username)  # The shop will award some BitCoin to new user

            with open('userlist.pkl', 'wb') as f:
                pickle.dump(self.userList, f)

    def login(self, username=None):
        if not isinstance(username, str):
            username = str(username)  # Check username's data type
        if username not in self.userList.keys():
            print('User %s is not exist.' % username)
        else:
            self.currentUser = self.userList[username]  # Load username as current user

    def show_my_pet(self):
        path = self.currentUser['warehouse']  # Get user's pets' house address
        img_list = [i for i in os.listdir(path) if 'jpeg' in i]  # Read jpeg file list
        plt.figure(figsize=(8, 6))
        for idx in range(len(img_list)):
            plt.subplot(2, 2, idx+1)  # Maximum 4 pets
            plt.title('Index: %d' % idx)  # Show index as sub figures' title
            plt.axis('off')
            pet_address = os.path.join(path, img_list[idx])  # image's address
            img = plt.imread(pet_address)
            self.currentUser['pets']['%d' % idx] = pet_address  # Add address into a dictionary list
            plt.imshow(img)
        plt.show()
        plt.close()

    def sell(self, index):
        if not isinstance(index, str):
            index = str(index)
        if not os.path.exists(self.currentUser['pets'][index]):  # Check index pet is exist
            print('This pet #%s is not exist' % index)
        else:
            target_name = str(len(self.shelf_list))
            self.shelf_list[target_name] = {}
            shutil.copy(self.currentUser['pets'][index], os.path.join(self.shelf_dir, '%s.jpeg' % target_name))
            self.shelf_list[target_name]['address'] = self.currentUser['pets'][index]
            self.shelf_list[target_name]['publicKey'] = self.currentUser['publicKey']
            self.shelf_list[target_name]['status'] = 'OnSale'
            self.shelf_list[target_name]['price'] = '%.3f' % random.random()
            with open('shelf_list.pkl', 'wb') as f:
                pickle.dump(self.shelf_list, f)

    def check_exist(self):
        for target in self.shelf_list.keys():
            if not os.path.exists(self.shelf_list[target]['address']):
                self.shelf_list[target]['status'] = 'Sold'  # Set pets' status as sold if it is not exist

    def show_shelf(self):
        path = self.shelf_dir  # Shelf's address
        self.check_exist()
        img_list = ['%s.jpeg' % i for i in self.shelf_list.keys()]  # Read jpeg file list

        plt.figure(figsize=(12, 9))
        for idx in range(len(img_list)):
            plt.subplot(3, 3, idx+1)  # Maximum 9 pets
            plt.title('ID: %d, $%s, %s' % (idx, self.shelf_list[str(idx)]['price'], self.shelf_list[str(idx)]['status']))  # Show index as sub figures' title
            plt.axis('off')
            pet_address = os.path.join(path, img_list[idx])  # image's address
            img = plt.imread(pet_address)
            plt.imshow(img)
        plt.show()
        plt.close()

    def buy(self, index):
        if not isinstance(index, str):
            index = str(index)
        self.check_exist()
        if self.shelf_list[index]['status'] == 'Sold':
            print('This pet has been sold out')
        else:
            self.purchase(self.shelf_list[index])


    def purchase(self, target, private_key):
        sender_address = self.currentUser['publicKey']
        sender_private_key = private_key
        recipient_address = target['publicKey']
        value = target['price']
        transaction = Transaction(sender_address, sender_private_key, recipient_address, value)




class Blockchain(object):
    def __init__(self):
        self.transactions = []
        self.chain = []

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))


    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a transaction to transactions array if the signature verified
        """
        transaction = OrderedDict({'sender_address': sender_address,
                                    'recipient_address': recipient_address,
                                    'value': value})

        #  Reward for mining a block
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        #  Manages transactions from wallet to another wallet
        else:
            transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            if transaction_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False

    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the blockchain
        """
        block = {'block_number': len(self.chain) + 1,
                'timestamp': time(),
                'transactions': self.transactions,
                'nonce': nonce,
                'previous_hash': previous_hash}

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
        return block

    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self):
        """
        Proof of work algorithm
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty

    def valid_chain(self, chain):
        """
        check if a bockchain is valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            #print(last_block)
            #print(block)
            #print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            #Delete the reward transaction
            transactions = block['transactions'][:-1]
            # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

            last_block = block
            current_index += 1

        return True

if __name__ == '__main__':
    p = Shop()
    p.login('123')
    p.show_my_pet()
