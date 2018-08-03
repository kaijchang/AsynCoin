# AsynCoin

AsynCoin is a very in-progress build of a basic implementation of a cryptocurrency and a blockchain using Python's [asyncio](https://docs.python.org/3/library/asyncio.html).


## Requirements

`PyYAML` - Used for loading blockchain and key configuration data from `.yaml` files.

`ecdsa` - Used for signing and verifying transactions trustlessly.

`sanic` - Async compatible [web framework](https://github.com/channelcat/sanic) used to run nodes.

`aiohttp` - Used to make asynchronous HTTP requests to nodes.

`aioconsole` - Used to asynchronously get user input.


## Installation

```console
$ git clone https://github.com/kajchang/asyncoin.git
$ cd asyncoin
$ pip install -r requirements.txt
```


## How to Run a Node

```console
$ python3 run.py node
No key found in config.yaml, generating new keys.
Enter a Passphrase > passphrase_to_encrypt_key

Encrypted Private Key: w2NdDEie/W51U+qc9Wh2Cby6hThiEGShv9p2bDYFDfKC8R5wLRuyXt0rB6OuI8BhYh45TxlyYueBAXRjdvJHa8RA7hhISlj7VgNdYR0j884=
Address: 028cad48898e7a79db3e0b1948a64cd470a6401dfbb53cd12ac377ac246d6dc961d1c64f9d01b89575a7e334682f8079

Started Blockchain and Mined Genesis Block.
[2018-08-02 17:33:02 -0700] [2568] [INFO] Goin' Fast @ http://127.0.0.1:8000

(NODE) > 
```

You can copy and paste the encrypted private key to the `encrypted_private` field in `config/keys.yaml` for using later.

How to check address balances on your node:

```console
(NODE) > balance (automatically uses the generated or loaded address)
Balance: 50 (from genesis block reward)
```

or

```console
(NODE) > balance 028cad48898e7a79db3e0b1948a64cd470a6401dfbb53cd12ac377ac246d6dc961d1c64f9d01b89575a7e334682f8079
Balance: 50
```

How to mine on your node:

```console
(NODE) > mine (automatically uses the generated or loaded address)
Started mining task.
(NODE) > balance
Balance: 150
(NODE) > mine stop
Stopped mining task.
```

Exiting gracefully:

```console
(NODE) > exit
```