import asyncio
import unittest
import os

import sys

sys.path.append('..')

from asyncoin.cryptocurrency.blockchain import Blockchain
from asyncoin.cryptocurrency.keys import KeyPair


class Test_Blockchain(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.keys = KeyPair()
        self.blockchain = Blockchain(self.keys.address)

    def test_mining(self):
        async def mining():
            block = await self.blockchain.mine_block(self.keys.address)
            await self.blockchain.add_block(block)
            self.assertEqual(await self.blockchain.get_balance(self.keys.address), 100)

        self.loop.run_until_complete(mining())

    def test_sending(self):
        async def sending():
            transaction = self.keys.Transaction(
                to='myfriend', amount=49, fee=1, nonce=0)
            await self.blockchain.add_transaction(transaction)
            block = await self.blockchain.mine_block('miner')
            await self.blockchain.add_block(block)

            self.assertEqual(await self.blockchain.get_balance(self.keys.address), 0)
            self.assertEqual(await self.blockchain.get_balance('myfriend'), 49)
            self.assertEqual(await self.blockchain.get_balance('miner'), 51)

        self.loop.run_until_complete(sending())

    def tearDown(self):
        os.remove('blockchain.db')


if __name__ == '__main__':
    unittest.main()
