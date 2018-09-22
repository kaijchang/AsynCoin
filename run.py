# !/usr/bin/python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser

from asyncoin.network.node import Node

from asyncoin.cryptocurrency.keys import KeyPair
from asyncoin.utilities.encryption import encrypt


parser = ArgumentParser()
parser.add_argument('mode')
parser.add_argument('-port', type=int, default=8000)
parser.add_argument('-db', default='blockchain.db')
parser.add_argument('-sync', default=None)

args = parser.parse_args()

if args.mode.lower() == 'node':
    node = Node(args.port, args.db)
    node.run(args.sync)

elif args.mode.lower() == 'generate':
    pass_ = input('Enter a Passphrase > ')
    keys = KeyPair()
    encrypted_key = encrypt(pass_.encode(), keys.hexprivate.encode())
    print("""
Encrypted Private Key: {0}
Address: {1}
""".format(encrypted_key, keys.address))
