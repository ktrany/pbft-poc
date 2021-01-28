#!/bin/bash
# start node
python node/index.py --id 0 --host localhost --port 10000 --path ./log/node0.log --dockerFileLoc 'D:\projects\bachelor\demo-app' --pkLoc ./keys/pair0/private_key.pem --peerNodeAddrList localhost:10001 localhost:10002 localhost:10003
