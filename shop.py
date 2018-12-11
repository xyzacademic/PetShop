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
from customer import Customer
from transaction import Transaction
from bc_tools import Blockchain




MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 100
MINING_DIFFICULTY = 2

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
                print('Load shelf list from local file shelf_list.pkl' )
                self.shelf_list = pickle.load(f)
        else:
            self.shelf_list = {}  # Customer list

        if os.path.exists('publicKey') and os.path.exists('privateKey'):
            with open('publicKey', 'r') as f:
                self.publicKey = f.readline()
            with open('privateKey', 'r') as f:
                self.privateKey = f.readline()
        else:
            self.new_wallet()

        if os.path.exists('blockchain.pkl'):
            with open('blockchain.pkl', 'rb') as f:  # load
                print('Load block-chain list from local file userlist.pkl')
                self.blockchain = pickle.load(f)
                if not self.blockchain.valid_chain(self.blockchain.chain):
                    print('Block chain is invalid')
                else:
                    print('Block chain is valid')
        else:
            self.blockchain = Blockchain()  # Customer list
            self.blockchain.transactions.append(
                OrderedDict({'sender_address': MINING_SENDER,
                             'recipient_address': self.publicKey,
                             'value': MINING_REWARD})
            )
            self.blockchain.create_block(0, '00')

            self.save_blockchain()

    def save_blockchain(self):
        with open('blockchain.pkl', 'wb') as f:
            pickle.dump(self.blockchain, f)

    def mine(self):
        last_block = self.blockchain.chain[-1]
        nonce = self.blockchain.proof_of_work()

        # # We must receive a reward for finding the proof.
        # self.blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=blockchain.node_id,
        #                               value=MINING_REWARD, signature="")

        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        self.blockchain.create_block(nonce, previous_hash)
        self.save_blockchain()

    def new_wallet(self):
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()

        self.privateKey = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
        self.publicKey = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        with open('privateKey', 'w') as f:
            f.write(self.privateKey)

        with open('publicKey', 'w') as f:
            f.write(self.publicKey)

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
            self.award(username)  # The shop will award some BitCoin to new user

            with open('userlist.pkl', 'wb') as f:
                pickle.dump(self.userList, f)

    def award(self, username):
        sender_address = self.publicKey
        sender_private_key = self.privateKey
        recipient_address = self.userList[username]['publicKey']
        value = 0.5
        transaction = Transaction(sender_address, sender_private_key, recipient_address, value)
        self.blockchain.submit_transaction(sender_address, recipient_address, value, transaction.sign_transaction())
        self.mine()


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

    def buy(self, index, temp_key):
        if not isinstance(index, str):
            index = str(index)
        self.check_exist()
        if self.shelf_list[index]['status'] == 'Sold':
            print('This pet has been sold out')
            return None
        else:
            # Load private key
            # with open(os.path.join(self.currentUser['warehouse'], 'privateKey'), 'r') as f:
            #     temp_key = f.readline()
            if self.purchase(target=self.shelf_list[index], private_key=temp_key):
                shutil.move(self.shelf_list[index]['address'], self.currentUser['warehouse'])
                return True
            else:
                return False

    def purchase(self, target, private_key):
        sender_address = self.currentUser['publicKey']
        sender_private_key = private_key
        recipient_address = target['publicKey']
        value = target['price']
        transaction = Transaction(sender_address, sender_private_key, recipient_address, value)
        if self.blockchain.submit_transaction(sender_address, recipient_address, value, transaction.sign_transaction()):
            self.mine()
        else:
            print('Transaction failed')
            return False

        return True



# if __name__ == '__main__':
#     p = Shop()
#     p.register('123')
#     p.register('456')
#     p.login('123')
#     p.show_my_pet()
#     p.show_shelf()
#     p.sell('0')
#     p.sell('3')
#     p.login('456')
#     p.show_my_pet()
#     p.buy('2')
#     p.show_my_pet()
#     p.show_shelf()
