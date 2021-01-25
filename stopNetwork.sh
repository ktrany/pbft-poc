#!/bin/bash
# kill all processes by pid in ./tmp/pbft_poc.pidfile
cat ./tmp/pbft_poc.pidfile | awk -F'|' '{
  split($1, a, "[;=]");
  for(i in a){
      print "kill " a[i]
  }
}' | bash | exit

echo 'network has been shut down successfully '