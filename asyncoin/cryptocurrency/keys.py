# -*- coding: utf-8 -*-

import ecdsa

from asyncoin.cryptocurrency.transaction import Transaction


class Verifier:
    """Wrapper around ecdsa.VerifyingKey
    Attributes:
        public (ecdsa.VerifyingKey): verifying key derived from hexadecimal.
        address (str): hexadecimal representation of the verifying key.
    """
    def __init__(self, address):
        """
        Args:
            address (str): hexadecimal representation of a verifying key.
        """
        self.address = address
        self.public = ecdsa.VerifyingKey.from_string(bytes.fromhex(address))

    def verify(self, transaction):
        """Wrapper around ecdsa.VerifyingKey.verify.
        Args:
            transaction (Transaction): transaction object to verify.

        Returns:
            bool:
                False if the signature is invalid.
                True if the the signature is valid.
        """
        try:
            self.public.verify(bytes.fromhex(transaction.signature), transaction.hash.encode())
            return True

        except ecdsa.keys.BadSignatureError:
            return False


class KeyPair(Verifier):
    """Wrapper around ecdsa.VerifyingKey and ecdsa.SigningKey.
    Attributes:
        private (ecdsa.SigningKey): the signing key.
        public (ecdsa.VerifyingKey): the corresponding verifying key, derived from 'private'
        hexprivate (str): hexadecimal representation of the signing key.
        address (str): hexade represenation of the verifying key.
    """
    def __init__(self, private=None):
        if private is None:
            self.private = ecdsa.SigningKey.generate()

        else:
            self.private = ecdsa.SigningKey.from_string(bytes.fromhex(private))

        self.public = self.private.get_verifying_key()

        self.hexprivate = self.private.to_string().hex()
        self.address = self.public.to_string().hex()

    def sign(self, transaction):
        """Wrapper around ecdsa.SigningKey.sign.
        Args:
            transaction (Transaction): transaction object to verify.

        Returns:
            str : hexadecimal representation of the signature.
        """
        signature = self.private.sign(transaction.hash.encode())

        return signature.hex()

    def Transaction(self, **kwargs):
        """Wrapper around Transaction class that automatically signs and verifies.
        Args:
            kwargs: see Transaction

        Returns:
            Transaction: signed Transaction
        """

        kwargs['from_'] = self.address

        transaction = Transaction(**kwargs)
        transaction.signature = self.sign(transaction)

        return transaction
