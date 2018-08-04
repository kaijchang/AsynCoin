# -*- coding: utf-8 -*-

from sanic import Sanic, response
import logging

import aiohttp
import asyncio
from aioconsole import ainput

from json import loads
import time
import yaml

from asyncoin.cryptocurrency.blockchain import Blockchain
from asyncoin.cryptocurrency.block import Block
from asyncoin.cryptocurrency.transaction import Transaction
from asyncoin.cryptocurrency.keys import KeyPair

from asyncoin.utilities.encryption import decrypt, encrypt


class Peers:
    """A set of adjacent peers."""

    def __init__(self):
        self.peers = set()

    async def find_peers(self):
        """Ask all peers for their peers.
        Returns:
            list: a list of the urls of all known peers.
        """
        peers = []

        for peer in self.peers:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://{}/peers'.format(peer)) as response:
                    peers += await response.json()

        return peers

    async def broadcast_transaction(self, transaction):
        """Send all peers a transaction.
        Args:
            transaction (Transaction): transaction to send.
        """
        peers = list(self.peers)
        for peer in peers:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post('http://{}/transaction'.format(peer), data=repr(transaction)):
                        pass

            except aiohttp.client_exceptions.ClientConnectorError:
                self.peers.remove(peer)

    async def broadcast_block(self, block):
        """Send all peers a block.
        Args:
            block (Block): transaction to send.
        """
        peers = list(self.peers)
        for peer in peers:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post('http://{}/block'.format(peer), data=repr(block)):
                        pass

            except aiohttp.client_exceptions.ClientConnectorError:
                self.peers.remove(peer)

    async def find_longest_chain(self):
        """Find the longest chain.
        Returns:
            list: the longest chain of blocks.
        """
        heights = []
        peers = list(self.peers)
        for peer in peers:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://{}/height'.format(peer)) as response:
                        height = await response.text()
                        heights.append(int(height))

            except aiohttp.client_exceptions.ClientConnectorError:
                self.peers.remove(peer)

        if heights:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://{}/blocks'.format(list(self.peers)[heights.index(max(heights))])) as response:
                        blocks = await response.json()

                return [Block(json_dict=block) for block in blocks]

            except aiohttp.client_exceptions.ClientConnectorError:
                self.peers.remove(peer)

        return []


class Node(Sanic, Blockchain, Peers):
    """A Node the communicates over Http using Sanic and requests."""

    def __init__(self):
        Peers.__init__(self)
        Sanic.__init__(self, __name__)

        @self.route('/block', methods=['POST'])
        async def block(request):
            if request.body is None:
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

            try:
                block = Block(json_dict=loads(request.body.decode()))

            except KeyError:
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

            if self.verify_block(block):
                self.add_block(block)
                await self.broadcast_block(block)

                return response.json({'success': True}, headers={'Content-Type': 'application/json'})

            elif block.index > self.height + 1:
                self.replace_chain()

                return response.json({'success': True}, headers={'Content-Type': 'application/json'})

            return response.json({'success': False}, headers={'Content-Type': 'application/json'})

        @self.route('/transaction', methods=['POST'])
        async def transaction(request):
            if request.body is None:
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

            try:
                transaction = Transaction(
                    json_dict=loads(request.body.decode()))

            except KeyError:
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

            if not self.verify_transaction(transaction):
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

            self.add_transaction(transaction)
            await self.broadcast_transaction(transaction)

            return response.json({'success': True}, headers={'Content-Type': 'application/json'})

        @self.route('/getblock/<index:int>', methods=['GET'])
        def getblock(request, index):
            try:
                return response.text(repr(self.block_from_index(index)))

            except IndexError:
                return response.json({'success': False}, headers={'Content-Type': 'application/json'})

        @self.route('/getlastblock', methods=['GET'])
        def getlastblock(request):
            return response.json(loads(repr(self.last_block)), headers={'Content-Type': 'application/json'})

        @self.route('/blocks', methods=['GET'])
        def blocks(request):
            return response.json(loads(repr(self.blocks)), headers={'Content-Type': 'application/json'})

        @self.route('/peers', methods=['GET', 'POST'])
        def peers(request):
            if request.method == 'GET':
                return response.json(list(self.peers), headers={'Content-Type': 'application/json'})

            if request.method == 'POST':
                if request.body is None:
                    return response.json({'success': False}, headers={'Content-Type': 'application/json'})

                if request.body.decode() == self.url:
                    return response.json({'success': False}, headers={'Content-Type': 'application/json'})

                self.peers.add(request.body.decode())
                return response.json({'success': True}, headers={'Content-Type': 'application/json'})

        @self.route('/balance/<address>', methods=['GET'])
        def balance(request, address):
            return response.text(str(self.get_balance(address)))

        @self.route('/nonce/<address>', methods=['GET'])
        def nonce(request, address):
            return response.text(str(self.get_account_nonce(address)))

        @self.route('/pending', methods=['GET'])
        def pending(request):
            return response.text(repr(self.pending))

        @self.route('/config', methods=['GET'])
        def config(request):
            return response.json(self.config_, headers={'Content-Type': 'application/json'})

        @self.route('/difficulty', methods=['GET'])
        def difficulty(request):
            return response.text(str(self.difficulty))

        @self.route('/height', methods=['GET'])
        def height(request):
            return response.text(str(self.height))

    async def mine(self, reward_address, lowest_fee=1):
        """Asynchronous POW task."""
        n = 0
        while True:
            await asyncio.sleep(0)

            acceptable_transactions = [
                transaction for transaction in self.pending if transaction.fee >= lowest_fee]
            reward_transaction = Transaction(to=reward_address, from_='Network', amount=self.reward + sum(
                transaction.fee for transaction in acceptable_transactions), nonce=0, fee=0)

            block = Block(index=self.height, nonce=n, data=[
                          reward_transaction] + acceptable_transactions, previous_hash=self.last_block.hash, timestamp=time.time())

            if block.hash.startswith(self.difficulty * '1'):
                self.add_block(block)
                await self.broadcast_block(block)
                n = 0

            n += 1

    async def interface(self):
        """Asynchronous user input task."""
        logging.getLogger('root').setLevel('CRITICAL')
        logging.getLogger('sanic.error').setLevel('CRITICAL')
        logging.getLogger('sanic.access').setLevel('CRITICAL')

        loop = asyncio.get_event_loop()

        while True:
            cmd = await ainput('(NODE) > ')
            cmd = cmd.lower().split()

            if not cmd:
                pass

            elif cmd[0] == 'mine':
                if len(cmd) > 1:
                    if cmd[1] == 'stop':
                        try:
                            mining_task.cancel()
                            del mining_task
                            print('Stopped mining task.')

                        except NameError:
                            print('The node is not mining.')

                    else:
                        if 'mining_task' in locals():
                            print('The node is already mining.')

                        else:
                            mining_task = loop.create_task(self.mine(cmd[1]))
                            print('Started mining task.')

                else:
                    if 'mining_task' in locals():
                        print('The node is already mining.')

                    else:
                        mining_task = loop.create_task(self.mine(self.address))
                        print('Started mining task.')

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

                    balance = self.get_balance(keys.address)

                    if amount > balance:
                        print('You only have {}.'.format(balance))
                        continue

                    transaction = keys.Transaction(
                        to=to, amount=amount, fee=fee, nonce=self.get_account_nonce(keys.address))

                    print('Created Transaction {}'.format(transaction.hash))

                    self.add_transaction(transaction)
                    await self.broadcast_transaction(transaction)

                    print('Broadcasting transaction...')

                else:
                    print('No encrypted key found in keys.yaml.')

            elif cmd[0] == 'balance':
                if len(cmd) > 1:
                    print('Balance: {}'.format(self.get_balance(cmd[1])))

                else:
                    print('Balance: {}'.format(self.get_balance(self.address)))

            elif cmd[0] == 'exit':
                for task in asyncio.Task.all_tasks():
                    task.cancel()

                loop.stop()

    def run(self):
        """Spin up a blockchain and start the Sanic server."""
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

        Blockchain.__init__(self, genesis_address=keys.address)

        print('Started Blockchain and Mined Genesis Block.')

        self.address = keys.address

        loop = asyncio.get_event_loop()

        self.add_task(self.interface())

        loop.create_task(Sanic.create_server(self))

        loop.run_forever()
