#!/bin/bash
# start node
python node/index.py --id 1 --host localhost --port 10001 --path ./log/node1.log --pkLoc ./keys/pair1/private_key.pem --peerNodeAddrList localhost:10000 localhost:10002 localhost:10003
