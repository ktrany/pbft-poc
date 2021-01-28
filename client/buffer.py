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
        self.resultBuffer = asyncio.Queue()

    async def getLatestResult(self):
        # Get a "work item" out of the queue.
        message = await self.resultBuffer.get()
        log.debug(f'latest message = {message["phase"]} from Node {message["fromNode"]}')
        # Notify the queue that the "work item" has been processed.
        self.resultBuffer.task_done()
        return message

    async def addNewResult(self, message):
        await self.resultBuffer.put(message)
