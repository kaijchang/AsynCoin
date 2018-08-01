# -*- coding: utf-8 -*-

import time
import statistics
import yaml

from asyncoin.cryptocurrency.transaction import Transaction
from asyncoin.cryptocurrency.block import Block
from asyncoin.cryptocurrency.keys import Verifier

with open('./asyncoin/config/config.yaml') as config_file:
    config = yaml.load(config_file.read())


class Blockchain:
    """A Cryptocurrency blockchain.
    Attributes:
        difficulty (str): the mining difficulty of the blockchain that all blocks have to start with.
        reward (int): the amount of cryptocurrency units rewarded for each mined block.
        blocks (list): a list of all the blocks in the blockchain.
        pending (list): a list of all pending transactions.
    """

    def __init__(self, config_=config, genesis_address=None, blocks=None):
        """
        Args:
            blocks (list, optional): a list of blocks to start the blockchain on.
            genesis_address (str, optional): address for genesis block reward
        """
        self.config_ = config_

        self.difficulty = self.config_['INITIAL_DIFFICULTY']

        self.reward = self.config_['INITIAL_REWARD']

        self.pending = []

        if blocks:
            if self.is_valid_chain(blocks):
                self.blocks = []
                self.blocks.append(blocks[0])
                for block in blocks[1:]:
                    self.add_block(block, syncing=True)

        else:
            self.blocks = [self.mine_genesis_block(genesis_address)]

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

    def mine_block(self, reward_address, lowest_fee=1):
        """Mine a block.
        Args:
            reward_address (str): the address to send the block's rewards to.
            lowest_fee (int, optional): the lowest fee to accept.

        Returns:
            Block: the mined block.
        """
        acceptable_transactions = [
            transaction for transaction in self.pending if transaction.fee >= lowest_fee]
        n = 0
        reward_transaction = Transaction(to=reward_address, from_='Network', amount=self.reward + sum(
            transaction.fee for transaction in acceptable_transactions), nonce=0, fee=0)
        block = Block(index=self.height, nonce=n, data=[
                      reward_transaction] + acceptable_transactions, previous_hash=self.last_block.hash, timestamp=time.time())

        while not block.hash.startswith(self.difficulty * '1'):
            acceptable_transactions = [
                transaction for transaction in self.pending if transaction.fee >= lowest_fee]
            reward_transaction = Transaction(to=reward_address, from_='Network', amount=self.reward + sum(
                transaction.fee for transaction in acceptable_transactions), nonce=0, fee=0)
            n += 1
            block = Block(index=self.height, nonce=n, data=[
                          reward_transaction] + acceptable_transactions, previous_hash=self.last_block.hash, timestamp=time.time())

        return block

    def verify_block(self, block, syncing=False):
        """Verify a block.
        Args:
            block (Block): block to verify.
            syncing (bool, optional): whether or not to check the timestamp.

        Returns:
            True if the block is valid.
            False if the block is invalid.
        """
        difficulty_check = block.hash.startswith(self.difficulty * '1')
        hash_check = block.previous_hash == self.last_block.hash
        index_check = block.index == len(self.blocks)
        transaction_check = all(self.verify_transaction(
            transaction) for transaction in block[1:])
        reward_check = block[0].amount == self.reward + \
            sum(transaction.fee for transaction in block[1:])
        timestamp_check = block.timestamp > self.lowest_acceptable_timestamp and block.timestamp < time.time() + \
            7200

        if syncing:
            return all((difficulty_check, index_check, transaction_check, reward_check, hash_check))

        return all((difficulty_check, index_check, transaction_check, reward_check, timestamp_check, hash_check))

    def verify_genesis_block(self, genesis_block):
        """Verify a genesis block.
        Args:
            genesis_block (Block): genesis block to verify.

        Returns:
            True if the block is valid.
            False if the block is invalid.
        """
        return genesis_block.hash.startswith(self.difficulty * '1') and genesis_block.index == 0 and len(genesis_block.data) == 1 and genesis_block[0].amount == self.reward

    def verify_transaction(self, transaction):
        """Verify a transaction.
        Args:
            transaction (Transaction): transaction to verify.

        Returns:
            True if the transaction is valid.
            False if the transaction is invalid.
        """
        signature_check = Verifier(transaction.from_).verify(transaction)
        balance_check = self.get_balance(
            transaction.from_) >= transaction.amount + transaction.fee
        nonce_check = transaction.nonce == self.get_account_nonce(
            transaction.from_)

        return all((signature_check, balance_check, nonce_check))

    @staticmethod
    def is_valid_chain(chain):
        """Static method to check the validity of a chain."""
        blockchain = Blockchain()
        if blockchain.verify_genesis_block(chain[0]):
            blockchain.blocks[0] = chain[0]
            for block in chain[1:]:
                if not blockchain.add_block(block, syncing=True):
                    return False

        else:
            return False

        return True

    @property
    def height(self):
        return len(self.blocks)

    @property
    def last_block(self):
        return self.block_from_index(-1)

    def block_from_index(self, index):
        return self.blocks[index]

    def add_block(self, block, syncing=False):
        """Wrapper around self.verify_block that adds a block to the blockchain if it's valid."""
        if self.verify_block(block, syncing=syncing):
            self.blocks.append(block)

            for transaction in block:
                for t in self.pending:
                    if t.hash == transaction.hash:
                        self.pending.remove(t)

            if self.height % self.config_['DIFFICULTY_ADJUST'] == 0:
                time_delta = self.blocks[-self.config_['DIFFICULTY_ADJUST']
                                         ].timestamp - self.blocks[-1].timestamp

                if time_delta / self.config_['DIFFICULTY_ADJUST'] < self.config_['TIME_TARGET']:
                    self.difficulty += 1

                else:
                    self.difficulty -= 1

            if self.height % self.config_['REWARD_HALVING'] == 0:
                self.reward = self.reward / 2

            return True

        return False

    def add_transaction(self, transaction):
        """Wrapper around self.add_transaction that add a transactions to the mempool if it's valid."""
        if self.verify_transaction(transaction):
            self.pending.append(transaction)
            return True

        return False

    def get_balance(self, address):
        """Gets the balance of an address.

        Returns:
            int: the amount of units of cryptocurrency the address owns.
        """
        balance = 0

        for block in self.blocks:
            for transaction in block.data:
                if transaction.to == address:
                    balance += transaction.amount

                if transaction.from_ == address:
                    balance -= transaction.amount
                    balance -= transaction.fee

        return balance

    def get_account_nonce(self, address):
        """Gets the nonce of an address.

        Returns:
            int: the account's nonce.
        """
        return len([transaction for block in self.blocks for transaction in block if transaction.from_ == address])

    @property
    def lowest_acceptable_timestamp(self):
        """Gets the median timestamp of past 11 blocks.

        Returns:
            int: unix timestamp (lowest acceptable timestamp for new blocks)
        """
        if not self.blocks:
            return 0

        if self.height < 11:
            return statistics.median([block.timestamp for block in self.blocks])

        return statistics.median([block.timestamp for block in self.blocks[-11:]])

    # Special class methods

    def __iter__(self):
        return iter(self.blocks)

    def __getitem__(self, index):
        return self.block_from_index(index)

    def __len__(self):
        return len(self.blocks)
