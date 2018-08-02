# -*- coding: utf-8 -*-

import asyncio
from aioconsole import ainput

from asyncoin.utilities.encryption import encrypt

from asyncoin.network.node import Peers

from asyncoin.cryptocurrency.keys import KeyPair


class Client(Peers):
    def __init__(self):
        super(Client, self).__init__()

    async def interface(self):
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

            elif cmd[0] == 'exit':
                for task in asyncio.Task.all_tasks():
                    task.cancel()

                loop.stop()

    def start(self):
        loop = asyncio.get_event_loop()

        loop.create_task(self.interface())

        loop.run_forever()
