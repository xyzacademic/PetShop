# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:22:51 2018

@author: lile
"""

import tkinter as tk
import pickle
from shop import Shop

# users = {'hannibal':'123'}
#
# with open('users_pwd.pkl', 'wb') as f:
#     pwd = pickle.dump(users, f)

class DAPP:
    def __init__(self, root):
        with open('users_pwd.pkl','rb') as f:
            self.pwd = pickle.load(f)
        self.p = Shop()
        self.l1 = tk.Label(root, text="Account Number")
        self.l1.grid(row=0, column=0)
        self.l2 = tk.Label(root, text="Password")
        self.l2.grid(row=1, column=0)
        self.v1 = tk.StringVar()
        self.v2 = tk.StringVar()
        self.e1 = tk.Entry(root, textvariable=self.v1)
        self.e1.grid(row=0, column=1, padx=10, pady=5)
        self.e2 = tk.Entry(root, textvariable=self.v2, show="*")
        self.e2.grid(row=1, column=1, padx=10, pady=5)
        self.b1 = tk.Button(root, text="Login", width=10, command=self.home_page)
        self.b1.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.b2 = tk.Button(root, text="Sign up", width=10, command=self.sign_up)
        self.b2.grid(row=2, column=1, sticky=tk.E, padx=10, pady=5)
        
    def sign_up(self):
        sign = tk.Toplevel()
        sign.title('Sign Up')
        tk.Label(sign, text='Account Number').grid(row=0, column=0)
        tk.Label(sign, text='Password').grid(row=1, column=0)
        v_account = tk.StringVar()
        v_password = tk.StringVar()
        self.e_account = tk.Entry(sign, textvariable=v_account)
        self.e_account.grid(row=0, column=1, padx=10, pady=5)
        self.e_password = tk.Entry(sign, textvariable=v_password)
        self.e_password.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(sign, text="Submit", width=10, command=self.sign_up_verify)\
                 .grid(row=2, columnspan=3, sticky=tk.W, padx=80, pady=5)
 
    def sign_up_verify(self):
        if self.e_account.get() != '' and self.e_password.get() != '':
            self.p.register(self.e_account.get())
            self.pwd[self.e_account.get()] = self.e_password.get()
            with open('users_pwd.pkl', 'wb') as f:
                pickle.dump(self.pwd, f)
            sign_up_success = tk.Toplevel()
            tk.Label(sign_up_success, text='Sign up Successful! You can login now')\
                        .grid(row=0, column=0)
        else:
            fail = tk.Toplevel()
            tk.Label(fail, text = 'Account number and password are requested!').grid(row=0, column=0)
    
               
    def show_my_pets(self):
        self.p.show_my_pet()
    
    def show_shelf(self):
        self.p.show_shelf()
        
    def home_page(self):
        if self.e1.get() == '' or self.e2.get() == '':
            empty = tk.Toplevel()
            tk.Label(empty, text = 'Please input your Account Number and password!')\
                    .grid(row=0, column=0)
        elif self.p.userList.get(self.e1.get(), 0):
            if self.e2.get() == self.pwd[self.e1.get()]:
                self.p.login(self.e1.get())
                home = tk.Toplevel()
                home.title('Home')
                tk.Label(home, text="Hello " + self.e1.get() + "! Welcome to Pets shop!").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
                tk.Button(home, text="My pets", width=10, command=self.show_my_pets).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
                tk.Button(home, text="Shop's shelf", width=10, command=self.show_shelf).grid(row=1, column=2, sticky=tk.E, padx=10, pady=5)
                tk.Label(home, text="Input the index to buy a pet:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
                tk.Label(home, text="Input the index to sell a pet:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
                tk.Button(home, text="Request", command=self.buy_pets).grid(row=2, column=2, sticky=tk.E, padx=10, pady=5)
                tk.Button(home, text="Request", command=self.selling).grid(row=3, column=2, sticky=tk.E, padx=10, pady=5)
                index_buy = tk.StringVar()
                index_sell = tk.StringVar()
                self.e_buy = tk.Entry(home, textvariable=index_buy)
                self.e_sell = tk.Entry(home, textvariable=index_sell)
                self.e_buy.grid(row=2, column=1, sticky=tk.W, padx=0, pady=5)
                self.e_sell.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)
            else:
                wrong_pwd = tk.Toplevel()
                tk.Label(wrong_pwd, text='The password is wrong!').grid(row=0, column=0)    
        else:
            not_user = tk.Toplevel()
            tk.Label(not_user, text = 'Account Number and password cannot match!').grid(row=0, column=0)
    
    def selling(self):
        if self.e_sell.get() not in self.p.currentUser['pets'].keys():
            no_such_pet = tk.Toplevel()
            no_such_pet.title('There is no such pet.')
            tk.Label(no_such_pet, text='There is no such pet.').grid(row=0, column=1)
        else:
            selling = tk.Toplevel()
            selling.title('Pets on sale!')
            tk.Label(selling, text='Your pet is on sale now.').grid(row=0, column=0)
            self.p.sell(self.e_sell.get())
            
    def buy_pets(self):
        if self.e_buy.get() not in self.p.shelf_list.keys():
            no_such_pet = tk.Toplevel()
            no_such_pet.title('There is no such pet!')
            tk.Label(no_such_pet, text='There is no such pet, you can buy another one.')\
                        .grid(row=0, column=0)
        elif self.p.shelf_list[self.e_buy.get()]['status'] == 'Sold':
            sold = tk.Toplevel()
            sold.title('This pet is sold.')
            tk.Label(sold, text='This pet has been sold, you can buy another one.')\
                        .grid(row=0, column=0)
        else:    
            trans = tk.Toplevel()
            trans.title('Transaction page')
            tk.Label(trans, text='The price is $' + self.p.shelf_list[self.e_buy.get()]['price'] + '.')\
                        .grid(row=0, column=0)
            tk.Label(trans, text="Recipient's public key").grid(row=1, column=0)
            tk.Label(trans, text="Your public key:").grid(row=2, column=0)
            tk.Label(trans, text="Your pravite key:").grid(row=3, column=0) 
            pra_key = tk.StringVar()
            self.e_add = tk.Entry(trans)#, textvariable=address)
            self.e_pub_key = tk.Entry(trans)#, textvariable=pub_key)
            self.e_pra_key = tk.Entry(trans, textvariable=pra_key, show="*")
            self.e_add.grid(row=1, column=1, padx=10, pady=5)
            self.e_add.delete(0, tk.END)
            self.e_add.insert(0,self.p.shelf_list[self.e_buy.get()]['publicKey'])
            self.e_pub_key.grid(row=2, column=1, padx=10, pady=5)
            self.e_pub_key.delete(0, tk.END)
            self.e_pub_key.insert(0, self.p.currentUser['publicKey'])
            self.e_pra_key.grid(row=3, column=1, padx=10, pady=5)
            tk.Button(trans, text="Submit", width=10, command=self.bought)\
                         .grid(row=4, columnspan=3, sticky=tk.W, padx=100, pady=5)


    def bought(self):
        verify = self.p.buy(self.e_buy.get(), self.e_pra_key.get())
        if verify:
            success = tk.Toplevel()
            tk.Label(success, text='Transaction is successful!').grid(row=0, column=0)
        else:
            error = tk.Toplevel()
            tk.Label(error, text='Sorry! Transaction Failed!').grid(row=0, column=0)
            
            
def main():
    root = tk.Tk()
    root.title('login')
    app = DAPP(root)
    root.mainloop()
    
if __name__ == '__main__':
    main()