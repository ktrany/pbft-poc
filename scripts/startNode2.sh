#!/bin/bash
# start node
python node/index.py --id 2 --host localhost --port 10002 --path ./log/node2.log --dockerFileLoc 'D:\projects\bachelor\demo-app' --pkLoc ./keys/pair2/private_key.pem --peerNodeAddrList localhost:10000 localhost:10001 localhost:10003
