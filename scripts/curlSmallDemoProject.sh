#!/bin/bash
curl --header "Content-Type: application/json" --request POST --data '{"branch":"feature", "repoCloneUrl":"https://github.com/ktrany/pbftTestProject.git"}' http://localhost:8080/webHook