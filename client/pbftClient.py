#! /usr/bin/env python3
import asyncio
from buffer import MessageBuffer
from cryptoHelper import CryptoHelper
from loggerWrapper import LoggerWrapper
import index
import json
import os
from pbftRequest import PBFTRequest
import time


log = LoggerWrapper(__name__, index.PATH).logger
REQUEST = 'Request'
RESULT = 'Result'

class PbftClient:
    
    def __init__(self, pbftHost, pbftPort):
        self.resultBuffer = MessageBuffer()
        self.cryptoHelper = CryptoHelper()
        self.pbftHost = pbftHost
        self.pbftPort = pbftPort
        self.maxFaultyNodes = 1

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
        await self.handleRetrievedMessage(message)

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

    async def handleRetrievedMessage(self, message):
        messageType = message['phase']

        if messageType == RESULT:
            log.debug('Write to ResultBuffer')
            await self.resultBuffer.addNewResult(message)
    
    # -------------------------------------------------------------------------
    #   A L G O R I T H M   S E C T I O N
    # -------------------------------------------------------------------------

    async def doRequest(self, operation):
        start = time.perf_counter()
        timestamp = time.time().__str__()
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

        # TODO: Retry if sent was not successful
        await self.send('localhost:10000', request)

        sameResultMessages = 0
        result = ''
        resultList = []

        log.info(f'A total of {self.maxFaultyNodes + 1} result messages are required ...')
        while not self.__isCommitted(sameResultMessages):
            log.info('Waiting for result message ...')
            resultMessage = await self.resultBuffer.getLatestResult()
            log.debug(f'Retrieved message: {resultMessage}')
            
            # TODO: check signature
            if resultMessage['timestamp'] == timestamp:
                
                if len(resultList) == 0:
                    resultList.append(resultMessage)

                else:
                    # check unique signatures
                    curSignature = resultMessage['signature']
                    if not any(element['signature'] == curSignature for element in resultList):
                        resultList.append(resultMessage)

                    # check same result
                    sameResultMessages, result = self.__checkDuplicateResults(resultList)
            # END IF
        # END WHILE
        log.info(f'accepted result is: {result}')
        end = time.perf_counter()
        log.info(f'Time Req accepted\t {end - start} s')
        self.__writeResultToFile(result, timestamp)
        end = time.perf_counter()
        log.info(f'Time Write to file\t {end - start} s')
                

    def __isCommitted(self, sameResults):
        ''' A result of a request is considered committed-local if
        f + 1 result messages from different nodes has been received
        '''
        return sameResults >= self.maxFaultyNodes + 1

    def __checkDuplicateResults(self, resultList):
        ''' A result of a request is accepted if
        f + 1 result messages from different nodes are equal
        '''
        sameResultMessages = 0
        result = None

        for i in resultList:
            if self.__isCommitted(sameResultMessages):
                result = i['result']
                break
            else:
                sameResultMessages = 0
            
            # Problem: Time executed is logged -> Logs are not deterministic and can't be compared
            # Workaround: Compare return code ...
            curResultHash = self.cryptoHelper.getDigest(f"{i['result']['returncode']}-{i['result']['stdout']}".encode('utf8'))

            for x in resultList:
                compareHash = self.cryptoHelper.getDigest(f"{x['result']['returncode']}-{x['result']['stdout']}".encode('utf8'))

                if curResultHash == compareHash:
                    sameResultMessages += 1

                log.debug(f'sameResultMessages: {sameResultMessages}')
                if self.__isCommitted(sameResultMessages):
                    break
        
        return sameResultMessages, result

    def __writeResultToFile(self, result, timestamp):
        
        fileName = f"./output/{timestamp}.log"
        
        # create dir if it does not exist yet
        outputDir = os.path.dirname(fileName)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
            
        log.info(f'Write result to {fileName}')
        with open(fileName, "w", encoding='utf-8') as textFile:
            textFile.write(result['stdout'])
            textFile.write(result['stderr'])
            