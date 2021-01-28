#! /usr/bin/env python3

REQUEST = 'Request'
PRE_PREPARE = 'PrePrepare' 
PREPARE = 'Prepare' 
COMMIT = 'Commit' 
RESULT = 'Result' 
VIEW_CHANGE = 'ViewChange' 
NEW_VIEW = 'NewView' 

# Decouple actual message from preprepare message is highly recommended for optimization (etc. choice of protocol for small and big sized messages)
# Message is only in Preprepare for educational reasons!
class PBFTPreprepareMessage:
    '''
    Pre-prepare message
    '''
    def __init__(self, phase, viewNum, seqNum, digest, signature, message):
        self.phase = phase
        self.viewNum = viewNum
        self.seqNum = seqNum
        self.digest = digest
        self.signature = signature
        # Better use a separate message for the actual request
        self.message = message

    def __str__(self):
        return f'''
        (
            "self.phase" = {self.phase}
            "self.viewNum" = {self.viewNum}
            "self.seqNum" = {self.seqNum}
            "self.digest" = {self.digest}
            "self.signature" = {self.signature}
            "self.message" = {self.message}
        )
        '''

class PBFTMessage:
    '''
    Message object for Prepare and Commit
    '''
    def __init__(self, phase, viewNum, seqNum, digest, signature, fromNode):
        self.phase = phase
        self.viewNum = viewNum
        self.seqNum = seqNum
        self.digest = digest
        self.signature = signature
        self.fromNode = fromNode

    def __str__(self):
        return f'''
        (
            "self.phase" = {self.phase}
            "self.viewNum" = {self.viewNum}
            "self.seqNum" = {self.seqNum}
            "self.digest" = {self.digest}
            "self.signature" = {self.signature}
            "self.fromNode" = {self.fromNode}
        )
        '''

class PBFTResultMessage:
    '''
    Message object for result
    '''
    def __init__(self, viewNum, timestamp, toClientHost, toClientPort, fromNode, result, signature):
        self.phase = RESULT
        self.viewNum = viewNum
        self.timestamp = timestamp
        self.toClientHost = toClientHost
        self.toClientPort = toClientPort
        self.fromNode = fromNode
        self.result = result
        self.signature = signature

    def __str__(self):
        return f'''
        (
            "self.phase" = {self.phase}
            "self.viewNum" = {self.viewNum}
            "self.timestamp" = {self.timestamp}
            "self.fromNode" = {self.fromNode}
            "self.result" = {self.result}
            "self.signature" = {self.signature}
        )
        '''