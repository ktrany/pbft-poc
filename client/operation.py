#! /usr/bin/env python3
import json

class Operation:

    def __init__(self, dockerfileStr, targetBranch):
        self.dockerfileStr = dockerfileStr
        self.targetBranch = targetBranch

    def toJsonString(self):
        return json.dumps(self.__dict__)
