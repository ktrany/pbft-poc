#! /usr/bin/env python3
import asyncio
from cryptoHelper import CryptoHelper
from loggerWrapper import LoggerWrapper
import index
import json
from pbftRequest import PBFTRequest
import time


log = LoggerWrapper(__name__, index.PATH).logger
REQUEST = 'Request'

class PbftClient:
    
    def __init__(self, pbftHost, pbftPort):
        self.cryptoHelper = CryptoHelper()
        self.pbftHost = pbftHost
        self.pbftPort = pbftPort

    # -------------------------------------------------------------------------
    #   P B F T     N E T W O R K   S E C T I O N
    # -------------------------------------------------------------------------

    # Socket Server
    async def receiveData(self, reader, writer):
        data = await reader.read()
        message = json.loads(data)
        addr = writer.get_extra_info('peername')

        log.debug(f"Received {message} from {addr}")

        log.debug("Close the connection")
        writer.close()
        # await self.handleRetrievedMessage(message)

    async def listen(self):
        server = await asyncio.start_server(self.receiveData, self.pbftHost, self.pbftPort)

        addr = server.sockets[0].getsockname()
        log.info(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    # Socket Client
    async def doSend(self, target, message):
        targetHost, targetPort = tuple(target.split(':'))
        
        log.debug(f'Try connecting to {target} ...')
        reader, writer = await asyncio.open_connection(
            targetHost, int(targetPort))

        log.debug(f'Send: {message}')
        payload = json.dumps(message.__dict__)
        writer.write(payload.encode())
        await writer.drain()

        log.debug('Close the connection')
        writer.close()
        await writer.wait_closed()

    async def send(self, target, message):
        try:
            await self.doSend(target, message)
        except ConnectionRefusedError:
            log.error(f'Connection refused. Target endpoint {target} unavailable ...')
            return
        except ConnectionResetError:
            log.error(f'Connection to target endpoint {target} was closed unexpectedly ...')
            return
        except ConnectionError:
            log.error(f'Connection to target endpoint {target} failed ...')
            return

    async def doRequest(self):
        while True:
            operation = 'echo hi from client'
            timestamp = time.time()
            signature = self.cryptoHelper.signRequest(
                phase = REQUEST,
                operation= operation,
                timestamp = timestamp,
                clientHost = self.pbftHost, 
                clientPort = self.pbftPort,
            )

            request = PBFTRequest(
                phase = REQUEST,
                operation= operation,
                timestamp = timestamp,
                clientHost = self.pbftHost, 
                clientPort = self.pbftPort,
                signature = signature,
                )
            await self.send('localhost:10000', request)
            await asyncio.sleep(10)
            