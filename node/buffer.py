#! /usr/bin/env python3
import asyncio
import index
from loggerWrapper import LoggerWrapper

log = LoggerWrapper(__name__, index.PATH).logger

class MessageBuffer:
    '''
    Buffer messages in queue for communication between " the socket server infinite loop"
    and "the algorithm infinite loop"
    '''
    def __init__(self):
        self.requestBuffer = asyncio.Queue()
        self.prePrepareBuffer = asyncio.Queue()
        self.prepareBuffer = asyncio.Queue()
        self.commitBuffer = asyncio.Queue()

    # Request
    async def getLatestRequest(self):
        # Get a "work item" out of the queue.
        message = await self.requestBuffer.get()
        log.debug(f'latest message = {message["phase"]} in from {message["clientHost"]}:{message["clientPort"]}')
        # Notify the queue that the "work item" has been processed.
        self.requestBuffer.task_done()
        return message

    async def addNewRequest(self, message):
        await self.requestBuffer.put(message)

    # Pre-prepare
    async def getLatestPrePrepare(self):
        # Get a "work item" out of the queue.
        message = await self.prePrepareBuffer.get()
        log.debug(f'latest message = {message["phase"]} in view = {message["viewNum"]}, seq = {message["seqNum"]}')
        # Notify the queue that the "work item" has been processed.
        self.prePrepareBuffer.task_done()
        return message

    async def addNewPrePrepare(self, message):
        await self.prePrepareBuffer.put(message)

    # Prepare
    async def getLatestPrepare(self):
        message = await self.prepareBuffer.get()
        log.debug(f'latest message = {message["phase"]} from node {message["fromNode"]} in view = {message["viewNum"]}, seq = {message["seqNum"]}')
        self.prepareBuffer.task_done()
        return message

    async def addNewPrepare(self, message):
        await self.prepareBuffer.put(message)
    
    # Commit
    async def getLatestCommit(self):
        message = await self.commitBuffer.get()
        log.debug(f'latest message = {message["phase"]} from node {message["fromNode"]} in view = {message["viewNum"]}, seq = {message["seqNum"]}')
        self.commitBuffer.task_done()
        return message

    async def addNewCommit(self, message):
        await self.commitBuffer.put(message)