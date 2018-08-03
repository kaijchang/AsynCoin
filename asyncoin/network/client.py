# -*- coding: utf-8 -*-

import asyncio
from aioconsole import ainput
import aiohttp

import random

from asyncoin.utilities.encryption import encrypt

from asyncoin.network.node import Peers

from asyncoin.cryptocurrency.keys import KeyPair


class Client(Peers):
    def __init__(self):
        super(Client, self).__init__()

    async def interface(self):
        """Asynchronous user input task."""
        loop = asyncio.get_event_loop()
        while True:
            cmd = await ainput('(CLIENT) > ')
            cmd = cmd.lower().split()

            if not cmd:
                pass

            elif cmd[0] == 'generate':
                pass_ = await ainput('Enter a Passphrase > ')
                keys = KeyPair()

                print(
                    """
Encrypted Private Key: {0}
Address: {1}
""".format(encrypt(pass_.encode(), keys.hexprivate.encode()), keys.address))

            elif cmd[0] == 'balance':
                if len(cmd) > 1:
                    balance = await self.get('balance/{}'.format(cmd[1]))
                    print('Balance: {}'.format(balance))

                else:
                    print("The 'balance' function requires two arguments.")

            elif cmd[0] == 'exit':
                for task in asyncio.Task.all_tasks():
                    task.cancel()

                loop.stop()

    async def connect(self):
        """Try to connect to nodes."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://127.0.0.1:8000/'):
                    self.peers.add('127.0.0.1:8000')

                    peers = await self.find_peers()

                    for peer in peers:
                        self.peers.add(peer)

        except aiohttp.client_exceptions.ClientConnectorError:
            pass

    async def get(self, endpoint):
        try:
            async with aiohttp.ClientSession() as session:
                peer = random.choice(list(self.peers))
                async with session.get('http://{0}/{1}'.format(peer, endpoint)) as response:
                    return await response.text()

        except aiohttp.client_exceptions.ClientConnectorError:
            self.peers.remove(peer)
            return await self.get(endpoint)

        except IndexError:
            await self.connect()

            if not self.peers:
                print('You have no peers.')

            else:
                return await self.get(endpoint)

    def start(self):
        loop = asyncio.get_event_loop()

        loop.create_task(self.connect())
        loop.create_task(self.interface())

        loop.run_forever()
