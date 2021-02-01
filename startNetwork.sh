#!/bin/bash
echo start network ...
# empty the pid
mkdir -p tmp
> ./tmp/pbft_poc.pidfile

# start nodes
'C:\Program Files\Git\git-bash.exe' -c ./scripts/startNode0.sh & > /dev/null 2&>1
echo $! >> ./tmp/pbft_poc.pidfile
sleep 1
'C:\Program Files\Git\git-bash.exe' -c ./scripts/startNode1.sh & > /dev/null 2&>1
echo $! >> ./tmp/pbft_poc.pidfile
sleep 1
'C:\Program Files\Git\git-bash.exe' -c ./scripts/startNode2.sh & > /dev/null 2&>1
echo $! >> ./tmp/pbft_poc.pidfile
sleep 1
'C:\Program Files\Git\git-bash.exe' -c ./scripts/startNode3.sh & > /dev/null 2&>1
echo $! >> ./tmp/pbft_poc.pidfile

echo network has been started successfully ...