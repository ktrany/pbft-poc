#! /usr/bin/env python3
import pbftPhase

class PBFTServiceState:

    def __init__(self, seqNum = 0, viewNum = 0, curDigest = ''):
        self.phase = pbftPhase.IDLE
        self.seqNum = seqNum
        self.viewNum = viewNum
        self.curDigest = curDigest

    def incrementSeqNum(self):
        self.seqNum += 1

    def incrementViewNum(self):
        self.viewNum += 1

    def updateSeqNum(self, value):
        self.seqNum = value

    def updateViewNum(self, value):
        self.viewNum = value

    def updateCurDigest(self, value):
        self.curDigest = value

    def __str__(self):
        return f'''
            (
                "self.phase": {self.phase},
                "self.view_num": {self.viewNum},
                "self.seq_num": {self.seqNum},
            )
            '''