#! /usr/bin/env python3

import index
from loggerWrapper import LoggerWrapper

log = LoggerWrapper(__name__, index.PATH).logger

class MessageLog:
    '''
    only in-memory for now
    '''

    def __init__(self):
        # only for primary
        self.requestLog = {}
        # only for backups
        self.prePrepareLog = {}
        self.prepareLog = {}
        self.commitLog = {}
        self.resultLog = {}

    # PrePrepare
    def getRequestKey(self, request):
        return f'{request["operation"]}-{request["timestamp"]}-{request["operation"]}-{request["clientHost"]}:{request["clientPort"]}'

    def addToRequestLog(self, key, value):
        self.requestLog[key] = value
        log.debug(f'key={key}, value={value} added to request log')

    def existsInRequestLog(self, key):
        if key in self.requestLog:
            return True
        else:
            return False
    
    # PrePrepare
    def getPrePrepareKey(self, pbftServiceState):
        return f'{pbftServiceState.viewNum}-{pbftServiceState.seqNum}'

    def addToPrePrepareLog(self, key, value):
        self.prePrepareLog[key] = value
        log.debug(f'key={key}, value={value} added to pre-prepare log')

    def existsInPrePrepareLog(self, key):
        if key in self.prePrepareLog:
            return True
        else:
            return False

    # TODO: use the other logs
    # Prepare
    def addToPrepareLog(self, key, value):
        self.prepareLog[key] = value

    def existsInPrepareLog(self, key):
        if key in self.prepareLog:
            return True
        else:
            return False

    # Commit
    def addToCommitLog(self, key, value):
        self.commitLog[key] = value

    def existsInCommitLog(self, key):
        if key in self.commitLog:
            return True
        else:
            return False

    # Result
    def addToResultLog(self, key, value):
        self.resultLog[key] = value

    def existsInResultLog(self, key):
        if key in self.resultLog:
            return True
        else:
            return False


    # TODO: check signatures in request and preprepare request are correct
    # TODO: d is the digest of m
    # check is in current view
    # TODO: has not already accepted request with same view and seqNum, but different d

