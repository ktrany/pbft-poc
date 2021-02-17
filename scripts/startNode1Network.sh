#!/bin/bash
# start node
python3.9 node/index.py --id 0 --host 0.0.0.0 --port 10001 --path ./log/node1.log --pkLoc ./keys/pair1/private_key.pem --peerNodeAddrList 172.24.100.78:10000 172.24.100.162:10002 172.24.100.168:10003
