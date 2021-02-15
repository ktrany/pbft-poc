#!/bin/bash
# start node
python3.9 node/index.py --id 0 --host localhost --port 10000 --path ./log/node0.log --pkLoc ./keys/pair0/private_key.pem --peerNodeAddrList 172.24.100.66:10001 172.24.100.162:10002 172.24.100.168:10003
