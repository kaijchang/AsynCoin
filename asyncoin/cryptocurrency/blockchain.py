# -*- coding: utf-8 -*-

import time
import statistics
import yaml
import os
import decimal

import asyncio
import aiosqlite

from asyncoin.cryptocurrency.transaction import Transaction
from asyncoin.cryptocurrency.block import Block
from asyncoin.cryptocurrency.keys import Verifier

with open(os.path.join(os.path.dirname(__file__), os.pardir, 'config/config.yaml')) as config_file:
    config = yaml.load(config_file.read())

with open(os.path.join(os.path.dirname(__file__), os.pardir, 'sql/startup.sql')) as script:
    startup_script = script.read()

with open(os.path.join(os.path.dirname(__file__), os.pardir, 'sql/block_template.sql')) as script:
    block_template = script.read()

with open(os.path.join(os.path.dirname(__file__), os.pardir, 'sql/transaction_template.sql')) as script:
    transaction_template = script.read()


class Blockchain:
    """A Cryptocurrency blockchain."""

    def __init__(self, genesis_address=None, config_=config, db='blockchain.db'):
        """
        Args:
            genesis_address (str, optional): address for genesis block reward.
            config (dict, optional): configuration for your blockchain.
        """
        self.config_ = config_

        self.difficulty = self.config_['INITIAL_DIFFICULTY']

        self.reward = self.config_['INITIAL_REWARD']

        self.pending = []

        self.db = db

        if not os.path.exists(self.db):
            asyncio.get_event_loop().run_until_complete(
                self.start_db(genesis_address))

    async def start_db(self, genesis_address):
        async with aiosqlite.connect(self.db) as db:
            await db.executescript(startup_script)
            block = self.mine_genesis_block(genesis_address)
            await db.execute(block_template, (block.index, block.hash, block.nonce, block.previous_hash, block.timestamp))
            await db.execute(transaction_template, (block.hash, block.data[0].hash, block.data[0].to, block.data[0].from_, block.data[0].amount, block.data[0].timestamp, block.data[0].signature, block.data[0].nonce, block.data[0].fee))
            await db.commit()

    def mine_genesis_block(self, genesis_address):
        """Mine the genesis block.
        Args:
            genesis_address (str): the address to send the first block's rewards to.

        Returns:
            Block : the mined genesis block.
        """
        n = 0
        reward_transaction = Transaction(
            to=genesis_address, from_='Network', amount=self.reward, nonce=0, fee=0)
        block = Block(index=0, nonce=n, data=[
                      reward_transaction], previous_hash=0, timestamp=time.time())

        while not block.hash.startswith(self.difficulty * '1'):
            n += 1
            block = Block(index=0, nonce=n, data=[
                          reward_transaction], previous_hash=0, timestamp=time.time())

        return block

    async def mine_block(self, reward_address, lowest_fee=1):
        """Mine a block.
        Args:
            reward_address (str): the address to send the block's rewards to.
            lowest_fee (int, optional): the lowest fee to accept.

        Returns:
            Block: the mined block.
        """
        n = 0
        while True:
            last_block = await self.last_block()
            await asyncio.sleep(0)

            acceptable_transactions = [
                transaction for transaction in self.pending if transaction.fee >= lowest_fee]
            reward_transaction = Transaction(to=reward_address, from_='Network', amount=self.reward + sum(
                transaction.fee for transaction in acceptable_transactions), nonce=0, fee=0)

            block = Block(index=await self.height(), nonce=n, data=[
                          reward_transaction] + acceptable_transactions, previous_hash=last_block.hash, timestamp=time.time())

            if block.hash.startswith(self.difficulty * '1'):
                return block

            n += 1

    async def verify_block(self, block):
        """Verify a block.
        Args:
            block (Block): block to verify.
            syncing (bool, optional): whether or not to check the timestamp.

        Returns:
            True if the block is valid.
            False if the block is invalid.
        """
        last_block = await self.last_block()
        difficulty_check = block.hash.startswith(self.difficulty * '1')
        hash_check = block.previous_hash == last_block.hash
        index_check = block.index == await self.height()
        transaction_check = all(await asyncio.gather(*[asyncio.ensure_future(self.verify_transaction(
            transaction)) for transaction in block[1:]])) if block[1:] else True
        reward_check = block[0].amount == self.reward + \
            sum(transaction.fee for transaction in block[1:])
        timestamp_check = block.timestamp > await self.lowest_acceptable_timestamp() and block.timestamp < time.time() + \
            7200

        return all((difficulty_check, index_check, transaction_check, reward_check, hash_check, timestamp_check))

    def verify_genesis_block(self, genesis_block):
        """Verify a genesis block.
        Args:
            genesis_block (Block): genesis block to verify.

        Returns:
            True if the block is valid.
            False if the block is invalid.
        """
        return genesis_block.hash.startswith(self.difficulty * '1') and genesis_block.index == 0 and len(genesis_block.data) == 1 and genesis_block[0].amount == self.reward

    async def verify_transaction(self, transaction):
        """Verify a transaction.
        Args:
            transaction (Transaction): transaction to verify.

        Returns:
            True if the transaction is valid.
            False if the transaction is invalid.
        """
        signature_check = Verifier(transaction.from_).verify(transaction)
        balance_check = await self.get_balance(
            transaction.from_) >= transaction.amount + transaction.fee
        nonce_check = transaction.nonce == await self.get_account_nonce(
            transaction.from_)
        decimal_check = decimal.Decimal(transaction.amount).as_tuple(
        ).exponent < 19 and decimal.Decimal(transaction.fee).as_tuple().exponent < 19

        return all((signature_check, balance_check, nonce_check, decimal_check))

    async def height(self):
        async with aiosqlite.connect(self.db) as db:
            async with db.execute('SELECT COUNT(*)\nFROM BLOCKS;') as cursor:
                result = await cursor.fetchone()
                return result[0]

    async def last_block(self):
        return await self.block_from_index(-1)

    async def block_from_index(self, index):
        if index > await self.height():
            raise IndexError

        if index >= 0:
            async with aiosqlite.connect(self.db) as db:
                async with db.execute('SELECT * FROM "BLOCKS" WHERE "NUMBER" = ?;', (str(index),)) as cursor:
                    block = await cursor.fetchone()

                async with db.execute('SELECT * FROM "TRANSACTIONS" WHERE "BLOCKHASH" = ?;', (block[1],)) as cursor:
                    transactions = await cursor.fetchall()

                return Block.from_tuple(block, transactions)

        else:
            return await self.block_from_index(await self.height() + index)

    async def blocks_from_range(self, start, end):
        height = await self.height()
        start = start if start >= 0 else height + start
        end = end if end >= 0 else height + end

        if end > height - 1 or start > height - 1 or start > end:
            raise IndexError

        async with aiosqlite.connect(self.db) as db:
            async with db.execute('SELECT * FROM "BLOCKS" WHERE "NUMBER" BETWEEN ? and ?', (start, end)) as cursor:
                blocks = await cursor.fetchall()
            hashes = tuple(block[1] for block in blocks)
            if len(hashes) == 1:
                async with db.execute('SELECT * FROM "TRANSACTIONS" WHERE "BLOCKHASH" = ?', (hashes[0],)) as cursor:
                    return [Block.from_tuple(blocks[0], await cursor.fetchall())]

            else:
                async with db.execute('SELECT * FROM "TRANSACTIONS" WHERE "BLOCKHASH" IN ({0}?)'.format('?,' * (len(blocks) - 1)), tuple(block[1] for block in blocks)) as cursor:
                    transactions = await cursor.fetchall()

                return [Block.from_tuple(block, tuple(transaction for transaction in transactions if transaction[0] == block[1])) for block in blocks]

    async def add_block(self, block):
        """Wrapper around self.verify_block that adds a block to the blockchain if it's valid."""
        if await self.verify_block(block):
            async with aiosqlite.connect(self.db) as db:
                await db.execute(block_template, (block.index, block.hash, block.nonce, block.previous_hash, block.timestamp))
                await db.executemany(transaction_template, [(block.hash, transaction.hash, transaction.to, transaction.from_, transaction.amount, transaction.timestamp, transaction.signature, transaction.nonce, transaction.fee) for transaction in block])
                for transaction in block:
                    for t in self.pending:
                        if t.hash == transaction.hash:
                            self.pending.remove(t)

                await db.commit()

            if await self.height() % self.config_['DIFFICULTY_ADJUST'] == 0:
                time_delta = self.blocks[-self.config_['DIFFICULTY_ADJUST']
                                         ].timestamp - self.blocks[-1].timestamp

                if time_delta / self.config_['DIFFICULTY_ADJUST'] < self.config_['TIME_TARGET']:
                    self.difficulty += 1

                else:
                    self.difficulty -= 1

            if await self.height() % self.config_['REWARD_HALVING'] == 0:
                self.reward = self.reward / 2

            return True

        return False

    async def add_transaction(self, transaction):
        """Wrapper around self.add_transaction that add a transactions to the mempool if it's valid."""
        if await self.verify_transaction(transaction):
            self.pending.append(transaction)
            return True

        return False

    async def get_balance(self, address):
        """Gets the balance of an address.

        Returns:
            int: the amount of units of cryptocurrency the address owns.
        """
        async with aiosqlite.connect(self.db) as db:
            async with db.execute('SELECT * FROM "TRANSACTIONS" WHERE "SENDER" = ? OR "RECEIVER" = ?', (address, address)) as cursor:
                transactions = [Transaction.from_tuple(transaction) for transaction in await cursor.fetchall()]

        balance = 0

        for transaction in transactions:
            if transaction.to == address:
                balance += transaction.amount

            if transaction.from_ == address:
                balance -= transaction.amount
                balance -= transaction.fee

        return balance

    async def get_account_nonce(self, address):
        """Gets the nonce of an address.

        Returns:
            int: the account's nonce.
        """
        async with aiosqlite.connect(self.db) as db:
            async with db.execute('SELECT COUNT(*) from "TRANSACTIONS" WHERE "SENDER" = ?', (address,)) as cursor:
                result = await cursor.fetchone()
                return result[0]

    async def lowest_acceptable_timestamp(self):
        """Gets the median timestamp of past 11 blocks.

        Returns:
            int: unix timestamp (lowest acceptable timestamp for new blocks)
        """
        height = await self.height()
        if height < 11:
            return statistics.median([block.timestamp for block in await self.blocks_from_range(0, height - 1)])

        return statistics.median([block.timestamp for block in await self.blocks_from_range(-11, height - 1)])
