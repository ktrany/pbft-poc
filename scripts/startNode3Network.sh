#!/bin/bash
# start node
python3.9 node/index.py --id 3 --host 0.0.0.0 --port 10003 --path ./log/node3.log --pkLoc ./keys/pair3/private_key.pem --peerNodeAddrList 172.24.100.78:10000 172.24.100.66:10001 172.24.100.162:10002
