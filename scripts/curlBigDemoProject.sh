#!/bin/bash
curl --header "Content-Type: application/json" --request POST --data '{"branch":"master", "repoCloneUrl":"https://github.com/ktrany/components.git"}' http://172.24.100.78:8080/webHook