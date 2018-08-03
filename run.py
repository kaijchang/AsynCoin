# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from asyncoin.network.node import Node
from asyncoin.network.client import Client

helptext = \
"""
======Usage======

python3 run.py node - Start a node.
python3 run.py client - Start a client.

=================
"""

if len(sys.argv) == 1:
    print(helptext)

elif sys.argv[1].lower() == 'client':
    client = Client()
    client.start()

elif sys.argv[1].lower() == 'node':
    node = Node()
    node.run()

else:
    print(helptext)
