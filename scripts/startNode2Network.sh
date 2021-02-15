#!/bin/bash
# start node
python3.9 node/index.py --id 2 --host 0.0.0.0 --port 10002 --path ./log/node2.log --pkLoc ./keys/pair2/private_key.pem --peerNodeAddrList 172.24.100.78:10000 172.24.100.66:10001 172.24.100.168:10003
