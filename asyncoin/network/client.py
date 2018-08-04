# -*- coding: utf-8 -*-

import asyncio
from aioconsole import ainput
import aiohttp

import random
import yaml

from asyncoin.utilities.encryption import encrypt, decrypt

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
                    balance = await self.get_balance(cmd[1])

                else:
                    balance = await self.get_balance(self.address)

                print('Balance: {}'.format(balance))

            elif cmd[0] == 'send':
                with open('./asyncoin/config/keys.yaml') as key_file:
                    enc_private = yaml.load(key_file.read())[
                        'encrypted_private']

                if enc_private:
                    pass_ = await ainput('Enter your Passphrase > ')
                    try:
                        keys = KeyPair(
                            decrypt(pass_.encode(), enc_private).decode())

                    except ValueError:
                        print('Unable to decrypt private key.')
                        continue

                    to = await ainput('Address to send to > ')
                    amount = await ainput('Amount to send > ')

                    try:
                        amount = int(amount)

                    except ValueError:
                        print("That's not a number.")
                        continue

                    fee = await ainput('Fee (at least 1) > ')

                    try:
                        fee = int(fee)

                    except ValueError:
                        print("That's not a number.")
                        continue

                    balance = await self.get_balance(keys.address)

                    if amount > balance:
                        print('You only have {}.'.format(balance))
                        continue

                    transaction = keys.Transaction(
                        to=to, amount=amount, fee=fee, nonce=await self.get_nonce(keys.address))

                    print('Created Transaction {}'.format(transaction.hash))

                    await self.broadcast_transaction(transaction)

                    print('Broadcasting transaction...')

                else:
                    print('No encrypted key found in keys.yaml.')

            elif cmd[0] == 'exit':
                for task in asyncio.Task.all_tasks():
                    task.cancel()

                loop.stop()

    async def connect(self, seed='127.0.0.1:8000'):
        """Try to connect to nodes."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://{}/'.format(seed)):
                    self.peers.add(seed)

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

    async def get_balance(self, address):
        balance = await self.get('balance/{}'.format(address))
        return int(balance)

    async def get_nonce(self, address):
        nonce = await self.get('nonce/{}'.format(address))
        return int(nonce)

    def start(self):
        with open('./asyncoin/config/keys.yaml') as key_file:
            enc_private = yaml.load(key_file.read())['encrypted_private']

        if enc_private:
            pass_ = input('Enter your Passphrase > ')
            try:
                keys = KeyPair(
                    decrypt(pass_.encode(), enc_private).decode())

            except ValueError:
                raise ValueError('Unable to decrypt private key.')

        else:
            print('No key found in keys.yaml, generating new keys.')
            pass_ = input('Enter a Passphrase > ')
            keys = KeyPair()
            print(
                """
Encrypted Private Key: {0}
Address: {1}
""".format(encrypt(pass_.encode(), keys.hexprivate.encode()), keys.address))

        self.address = keys.address

        loop = asyncio.get_event_loop()

        loop.create_task(self.connect())
        loop.create_task(self.interface())

        loop.run_forever()
