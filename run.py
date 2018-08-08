# !/usr/bin/python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser

from asyncoin.network.node import Node
from asyncoin.network.client import Client


parser = ArgumentParser()
parser.add_argument('mode')
parser.add_argument('-port', type=int, default=8000)
parser.add_argument('-db', default='blockchain.db')

args = parser.parse_args()

if args.mode.lower() == 'client':
    client = Client()
    client.start()

elif args.mode.lower() == 'node':
    node = Node(args.port, args.db)
    node.run()
