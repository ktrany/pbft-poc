#! /usr/bin/env python3
import json

class Operation:

    def __init__(self, repoCloneUrl, targetBranch):
        self.repoCloneUrl = repoCloneUrl
        self.targetBranch = targetBranch

    def toJsonString(self):
        return json.dumps(self.__dict__)
