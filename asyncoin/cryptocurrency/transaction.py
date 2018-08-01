# -*- coding: utf-8 -*-

from hashlib import sha256
import time
import json


class Transaction:
    """A Cryptocurrency transaction.
    Attributes:
        to (str): address that the transaction is to.
        from_ (str): address that the transaction is from.
        amount (int): the amount of cryptocurrency transacted.
        signature (str): hexadecimal representation of the signer's signature.
        hash (str): hexadecimal message digest of the transaction's content.
        fee (int): transaction fee paid to miners to prevent spam attack.
        nonce (int): account nonce to prevent replay attack.
    """
    def __init__(self, json_dict=None, **kwargs):
        """
        Args:
            json_dict (dict, optional): dictionary to load transaction data from.
            **kwargs:
                to (str): address that the transaction is to.
                from_ (str): address that the transaction is from.
                amount (int): the amount of cryptocurrency transacted.
                signature (str, optional): hexadecimal representation of the signer's signature.
                fee (int): transaction fee paid to miners to prevent spam attack.
                nonce (int): account nonce to prevent replay attack.
        """

        if json_dict is not None:
            self.to = json_dict['to']
            self.from_ = json_dict['from_']
            self.amount = json_dict['amount']
            self.timestamp = json_dict['timestamp']
            self.signature = json_dict['signature']
            self.nonce = json_dict['nonce']
            self.fee = json_dict['fee']

        elif kwargs:
            self.to = kwargs['to']
            self.from_ = kwargs['from_']
            self.amount = kwargs['amount']
            self.timestamp = kwargs.get('timestamp', time.time())
            self.signature = kwargs.get('signature')
            self.nonce = kwargs['nonce']
            self.fee = kwargs['fee']

    @property
    def hash(self):
        return sha256('{}{}{}{}{}{}'.format(self.to, self.from_, self.amount, self.fee, self.nonce, self.timestamp).encode()).hexdigest()

    # Special class methods

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        __dict__ = dict(self.__dict__)
        __dict__['hash'] = self.hash

        return json.dumps(__dict__)

    def __eq__(self, other):
        return self.hash == other.hash
