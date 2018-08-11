import asyncio
import unittest
import os

try:
    from asyncoin.cryptocurrency.blockchain import Blockchain
    from asyncoin.cryptocurrency.keys import KeyPair

except ModuleNotFoundError:
    import sys
    sys.path.append('..')
    from asyncoin.cryptocurrency.blockchain import Blockchain
    from asyncoin.cryptocurrency.keys import KeyPair


class Test_Blockchain(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.keys = KeyPair()
        self.blockchain = Blockchain(self.keys.address, db='test.db')

    def test_mining(self):
        async def mining():
            block = await self.blockchain.mine_block(self.keys.address)
            await self.blockchain.add_block(block)
            self.assertEqual(await self.blockchain.get_balance(self.keys.address), 100)

        self.loop.run_until_complete(mining())

    def test_sending(self):
        friend_address = KeyPair().address
        miner_address = KeyPair().address

        async def sending():
            transaction = self.keys.Transaction(
                to=friend_address, amount=49, fee=1, nonce=0)
            await self.blockchain.add_transaction(transaction)
            block = await self.blockchain.mine_block(miner_address)
            await self.blockchain.add_block(block)

            self.assertEqual(await self.blockchain.get_balance(self.keys.address), 0)
            self.assertEqual(await self.blockchain.get_balance(friend_address), 49)
            self.assertEqual(await self.blockchain.get_balance(miner_address), 51)

        self.loop.run_until_complete(sending())

    def tearDown(self):
        os.remove('test.db')


if __name__ == '__main__':
    unittest.main()
