# AsynCoin

[![Build Status](https://travis-ci.org/kajchang/AsynCoin.svg?branch=master)](https://travis-ci.org/kajchang/AsynCoin)

AsynCoin is a very in-progress build of a basic implementation of a cryptocurrency and a blockchain using Python's [AsyncIO](https://docs.python.org/3/library/asyncio.html).

## Table of Contents

[How to Run a Node](https://github.com/kajchang/asyncoin#how-to-run-a-node)

[Blockchain Explorer](https://github.com/kajchang/asyncoin#blockchain-explorer)

[Syncing a Node](https://github.com/kajchang/asyncoin#syncing-a-node)

## Getting Started

```bash
$ git clone https://github.com/kajchang/asyncoin.git
$ cd asyncoin
$ pip install -r requirements.txt
```


## How to Run a Node

```bash
$ python3 run.py generate
Enter a Passphrase > passphrase_to_encrypt_key

Encrypted Private Key: KbN/48CEbBeIcEykO/If4RXiCZvvVGMQ5cr4fKsMlzT0Qmuc3YefdBfJl/YrUQbhZ6qkEpQi3Q6pF8wpHU7odKoe0YxvNnQVWrildnGwr6Y=
Address: 9c9f3695ff837dd5c251666841b06cf9d5f25691efbc130ffcb4bd9856158a1a07e31c3574dc5f15859a8c1a2f7369fb

```

Fill out the fields of `keys.yaml` with the provided encrypted key and address.

```bash
$ python3 run.py node
Started Blockchain and Mined Genesis Block.
[2018-08-12 10:35:27 -0700] [8930] [INFO] Goin' Fast @ http://192.168.1.10:8000
(NODE) > 
```

Getting balance:

```bash
(NODE) > balance
Balance: 50 (from genesis block reward)
```

or

```bash
(NODE) > balance 9c9f3695ff837dd5c251666841b06cf9d5f25691efbc130ffcb4bd9856158a1a07e31c3574dc5f15859a8c1a2f7369fb
Balance: 50
```

Mining:

```bash
(NODE) > mine
Started mining task.
(NODE) > balance
Balance: 150
(NODE) > mine stop
Stopped mining task.
```

Sending:

```bash
(NODE) > send
Enter your Passphrase > passphrase_to_encrypt_key
Address to send to > beb55b6728e45e2cfd45e6c9a146e6693e74cd785dcc91bd7fd4135185d1fc6d0b0ad5c65742d34709a6165124f5ab14
Amount to send > 49
Fee (at least 1) > 1
Created Transaction 9d075e6ddb798d851a490abb28f5e2ffdc798b62f33322c01bd0987d42dbc355
Broadcasting transaction...
(NODE) > mine
Started mining task.
```

Wait a while to mine a block for your transaction to be included in the blockchain, then try checking the balance of 'beb55b6728e45e2cfd45e6c9a146e6693e74cd785dcc91bd7fd4135185d1fc6d0b0ad5c65742d34709a6165124f5ab14'.


## Syncing a Node

With another node running in a seperate terminal window, take the uri from the `[2018-08-02 17:33:02 -0700] [2568] [INFO] Goin' Fast @ http://192.168.1.5:8000` of that nodes' startup, and 

```bash
$ python3 run.py node -port 7999 -sync http://192.168.1.10:8000
```

Of course, logically replace the port with any open port, and the `-sync` argument with whatever comes in the startup line for the first node.


## Blockchain Explorer

![explorer.png](https://github.com/kajchang/AsynCoin/raw/master/assets/explorer.png)

This is an in-progress way to live monitor your blockchain in your browser. It uses websockets to subscribe to new blocks, and you can access it by opening the `index.html` file in the `explorer` folder in your browser or executing `open explorer/index.html`.

## Testing

```bash
$ python3 -m unittest discover
```

## TODO

- Finish Blockchain Explorer
- Implementations of features like checksummed addresses, merkle trees, mnemonics
- Move more of UI from cli -> web
- Dockerize?
