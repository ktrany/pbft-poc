#! /usr/bin/env python3

class PBFTRequest:
    def __init__(self, phase, operation, timestamp, clientHost, clientPort, signature):
        self.phase = phase
        self.operation = operation
        self.timestamp = timestamp
        self.clientHost = clientHost
        self.clientPort = clientPort
        self.signature = signature

    def __str__(self):
        return f'''
        (
            "self.phase" = {self.phase}
            "self.operation" = {self.operation}
            "self.timestamp" = {self.timestamp}
            "self.clientHost" = {self.clientHost}
            "self.clientPort" = {self.clientPort}
            "self.signature" = {self.signature}
        )
        '''