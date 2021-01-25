#!/bin/bash
# start node
python node/index.py --id 3 --host localhost --port 10003 --path ./log/node3.log --pkLoc ./keys/pair3/private_key.pem --peerNodeAddrList localhost:10000 localhost:10001 localhost:10002
