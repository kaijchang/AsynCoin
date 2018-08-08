# AsynCoin

AsynCoin is a very in-progress build of a basic implementation of a cryptocurrency and a blockchain using Python's [AsyncIO](https://docs.python.org/3/library/asyncio.html).

## Table of Contents

[How to Run a Node](https://github.com/kajchang/asyncoin#how-to-run-a-node)

[Blockchain Explorer](https://github.com/kajchang/asyncoin#blockchain-explorer)

## Getting Started

```bash
$ git clone https://github.com/kajchang/asyncoin.git
$ cd asyncoin
$ pip install -r requirements.txt
```


## How to Run a Node

```bash
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

Getting balance:

```bash
(NODE) > balance
Balance: 50 (from genesis block reward)
```

or

```bash
(NODE) > balance 028cad48898e7a79db3e0b1948a64cd470a6401dfbb53cd12ac377ac246d6dc961d1c64f9d01b89575a7e334682f8079
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
Address to send to > myfriend
Amount to send > 49
Fee (at least 1) > 1
Created Transaction a2f92410d8ccb475ff9f21568cef0f370a5d9eeb199ee43e34c085b196e8f0ee
Broadcasting transaction...
(NODE) > mine
Started mining task.
```

Wait a while to mine a block for your transaction to be included in the blockchain, then try checking the balance of 'myfriend'.

Exiting gracefully:

```bash
(NODE) > exit
```


## Blockchain Explorer

![explorer.png](https://github.com/kajchang/AsynCoin/raw/master/assets/explorer.png)

This is an in-progress way to live monitor your blockchain in your browser. It uses websockets to subscribe to new blocks, and you can access it by opening the `index.html` file in the `explorer` folder in your browser.

## Testing

```bash
$ python3 -m unittest discover
```

## TODO

- Finish Blockchain Explorer
- Implementations of features like checksummed addresses, merkle trees, mnemonics
- Finish syncing with other nodes
