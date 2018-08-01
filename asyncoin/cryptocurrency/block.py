# -*- coding: utf-8 -*-

from hashlib import sha256
import json

from asyncoin.cryptocurrency.transaction import Transaction


class Block:
    """A Cryptocurrency block.
    Attributes:
        index (int): the index of the block in the blockchain.
        nonce (int): arbitrary value used in proof of work.
        data (list): the list of data (transactions) contained in the block.
        previous_hash (str): the previous hash in the blockchain.
        timestamp (int): the time the block was created.
        hash (str): hexadecimal message digest of the block's contents.
    """
    def __init__(self, json_dict=None, **kwargs):
        """
        Args:
            json_dict(dict, optional): dictionary to load block data from.
            **kwargs:
                index (int): the index of the block in the blockchain.
                nonce (int): arbitrary value used in proof of work.
                data (list): the list of data (transactions) contained in the block.
                previous_hash (str): the previous hash in the blockchain.
                timestamp (int): the time the block was created.
        """
        if json_dict is not None:
            self.index = json_dict['index']
            self.nonce = json_dict['nonce']
            self.data = [Transaction(transaction) for transaction in json_dict['data']]
            self.previous_hash = json_dict['previous_hash']
            self.timestamp = json_dict['timestamp']

        elif kwargs:
            self.index = kwargs['index']
            self.nonce = kwargs['nonce']
            self.data = kwargs['data']
            self.previous_hash = kwargs['previous_hash']
            self.timestamp = kwargs['timestamp']

    @property
    def hash(self):
        return sha256('{}{}{}{}{}'.format(self.index, self.nonce, self.previous_hash, self.data, self.timestamp).encode()).hexdigest()

    # Special class methods

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        __dict__ = dict(self.__dict__)

        __dict__['data'] = [transaction.__dict__ for transaction in __dict__['data']]
        __dict__['hash'] = self.hash

        return json.dumps(__dict__)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __eq__(self, other):
        return self.hash == other.hash
