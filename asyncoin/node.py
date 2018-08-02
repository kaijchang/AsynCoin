# -*- coding: utf-8 -*-

from sanic import Sanic, response

from json import loads
import aiohttp
import asyncio

from asyncoin.cryptocurrency.blockchain import Blockchain
from asyncoin.cryptocurrency.block import Block
from asyncoin.cryptocurrency.transaction import Transaction


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

            except ConnectionRefusedError:
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

            except ConnectionRefusedError:
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

            except ConnectionRefusedError:
                self.peers.remove(peer)

        if heights:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://{}/blocks'.format(list(self.peers)[heights.index(max(heights))])) as response:
                        blocks = await response.json()

                return [Block(json_dict=block) for block in blocks]

            except ConnectionRefusedError:
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

    def run(self, genesis_address):
        """Spin up a blockchain and start the Sanic server.
        Args:
            genesis_address (str): address to mine the genesis block.
        """
        Blockchain.__init__(self, genesis_address=genesis_address)
        Sanic.run(self)
