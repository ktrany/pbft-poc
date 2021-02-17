#! /usr/bin/env python3
import asyncio
from buffer import MessageBuffer
from cryptoHelper import CryptoHelper
from executor import Executor
import index
import json
from loggerWrapper import LoggerWrapper
import pbftMessage
import pbftPhase
from pbftMessageLog import MessageLog
from pbftServiceState import PBFTServiceState
import random
import subprocess

log = LoggerWrapper(__name__, index.PATH).logger

class PBFTNode:

    def __init__(self, id, host, port, peerNodeList):
        # self.config = config
        self.messageBuffer = MessageBuffer()
        self.messageLog = MessageLog() # TODO: save all messages in Log. currently only the messages sent are saved (the received messages should be saved too!)
        self.cryptoHelper = CryptoHelper()
        self.executor = Executor()
        self.id = id 
        self.host = host
        self.port = port
        self.pbftServiceState = PBFTServiceState()
        self.peerNodeList = peerNodeList

        # N >= 3 f + 1
        # N - 1 >= 3 f
        # (N - 1)/3 >= f
        # and N = len(self.peerNodeList) + 1
        self.maxFaultyNodes = len(self.peerNodeList) // 3

        if self.maxFaultyNodes < 1:
            raise Exception('Not enough peer nodes for BFT provided')

    # -------------------------------------------------------------------------
    #   N E T W O R K   S E C T I O N
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
        server = await asyncio.start_server(self.receiveData, self.host, self.port)

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
        except OSError:
            log.error(f'{target} unreachable ...')
            return
        except:
            log.error(f'Someting went wrong ...')
            return

    async def broadcast(self, message):
        for peer in self.peerNodeList:
            await self.send(peer, message)

    # handler
    async def handleRetrievedMessage(self, message):
        messageType = message['phase']

        if messageType == pbftMessage.REQUEST:
            log.debug('Write to RequestBuffer')
            await self.messageBuffer.addNewRequest(message)
        elif messageType == pbftMessage.PRE_PREPARE:
            log.debug('Write to PrePrepareBuffer')
            await self.messageBuffer.addNewPrePrepare(message)
        elif messageType == pbftMessage.PREPARE:
            log.debug('Write to PrepareBuffer')
            await self.messageBuffer.addNewPrepare(message)
        elif messageType == pbftMessage.COMMIT:
            log.debug('Write to CommitBuffer')
            await self.messageBuffer.addNewCommit(message)
        else:
            log.error('Unknown message type received')

    # -------------------------------------------------------------------------
    #   A L G O R I T H M   S E C T I O N
    # -------------------------------------------------------------------------


    def isPrimary(self):
        '''
            According to the paper:
            p = v mod |R|
            with
            p: primary
            v: view number
            |R|: Total number of replicas in the network
        '''
        return self.id == self.pbftServiceState.viewNum % (len(self.peerNodeList) + 1)


    async def doOnePbftRound(self):
        while True:
            await asyncio.sleep(5)
            
            log.info('Heartbeat')

            await self.__handleClientRequest()

            await self.__handlePrePreparePhase()
            
            await self.__handlePreparePhase()

            await self.__handleCommitPhase()


    async def __handleClientRequest(self):
        if self.isPrimary():
            # wait for client request here
            log.info('Waiting for client request:')
            request = await self.messageBuffer.getLatestRequest()
            # if received:
            await self.__onRetrieveRequest(request)
        self.logCurrentState()


    async def __handlePrePreparePhase(self):
        if not self.isPrimary():
            log.info('Pre-Prepare phase:')
            log.info('Waiting for Pre-Prepare message ...')
            prePrepareMessage = await self.messageBuffer.getLatestPrePrepare()
            
            await self.__onRetrievePrePrepareMessage(prePrepareMessage)

    
    async def __handlePreparePhase(self):
        log.info('Prepare phase:')

        acceptedPrepareMessages = 0
        prepareList = []
        key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
        prePrepareMessage = self.messageLog.prePrepareLog[key]

        # primary does not sent a prepareMesage
        if not self.isPrimary():
            # check if self prepapreMessage satisfies predicate
            selfPrepareMessage = self.messageLog.prepareLog[key]
            if self.__shouldAccept(message=selfPrepareMessage, prePrepareMessage=prePrepareMessage):
                prepareList.append(selfPrepareMessage)
                acceptedPrepareMessages = len(prepareList)


        while not self.__isPrepared(acceptedPrepareMessages):
            log.info('Waiting for Prepare message ...')
            prepareMessage = await self.messageBuffer.getLatestPrepare()
            log.debug(f'Retrieved message: {prepareMessage}')
            log.info(f'{2 * self.maxFaultyNodes - acceptedPrepareMessages} additional prepare messages are required')
            if self.__shouldAccept(message=prepareMessage, prePrepareMessage=prePrepareMessage):
                prepareList.append(prepareMessage)
                acceptedPrepareMessages = len(prepareList)
        
        if self.__isPrepared(acceptedPrepareMessages):
            log.info(f'Message in view={self.pbftServiceState.viewNum}, seq={self.pbftServiceState.seqNum} is prepared')
            await self.__sendCommitMessage()


    async def __handleCommitPhase(self):
        log.info('Commit phase:')

        acceptedCommitMessages = 0
        commitList = []
        key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
        prePrepareMessage = self.messageLog.prePrepareLog[key]

        # check if self commitMessage satisfies predicate
        selfCommitMessage = self.messageLog.commitLog[key]
        if self.__shouldAccept(message=selfCommitMessage, prePrepareMessage=prePrepareMessage):
            commitList.append(selfCommitMessage)
            acceptedCommitMessages = len(commitList)

        while not self.__isCommittedLocal(acceptedCommitMessages):
            log.info('Waiting for Commit message ...')
            commitMessage = await self.messageBuffer.getLatestCommit()
            log.debug(f'Retrieved message: {commitMessage}')
            log.info(f'{2 * self.maxFaultyNodes - acceptedCommitMessages} additional commit messages are required')
            if self.__shouldAccept(message=commitMessage, prePrepareMessage=prePrepareMessage):
                commitList.append(commitMessage)
                acceptedCommitMessages = len(commitList)
        
        if self.__isCommittedLocal(acceptedCommitMessages):
            log.info(f'Message in view={self.pbftServiceState.viewNum} and seqNum={self.pbftServiceState.seqNum} is committed')
            log.info(f'Executing operation requested in view={self.pbftServiceState.viewNum}, seq={self.pbftServiceState.seqNum} ...')

            randomTagId = random.random()
            # execute the operation
            repoCloneUrl = prePrepareMessage['message']['operation']['repoCloneUrl']
            targetBranch = prePrepareMessage['message']['operation']['targetBranch']
            result = self.executor.runTask(
                repoCloneUrl = repoCloneUrl,
                targetBranch = targetBranch,
                imageTag = f'getting-started{index.ID}-{randomTagId}',
            )
            # Send the result to the client
            await self.__sendResultMessage(prePrepareMessage, result.__dict__)

    
    async def __onRetrieveRequest(self, request):       
        self.pbftServiceState.incrementSeqNum()
        key = self.messageLog.getRequestKey(request)
        self.messageLog.addToRequestLog(key = key, value = request)
        await self.__sendPrePrepareMessage(request)
    
    
    async def __onRetrievePrePrepareMessage(self, prePrepareMessage):       
        self.pbftServiceState.updateSeqNum(prePrepareMessage['seqNum'])
        self.pbftServiceState.updateCurDigest(prePrepareMessage['digest'])
        log.info(f'Handling request in view={self.pbftServiceState.viewNum}, seq={self.pbftServiceState.seqNum} in this round ...')

        if prePrepareMessage != None:
            key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
            self.messageLog.addToPrePrepareLog(key = key, value = prePrepareMessage)
            await self.__sendPrepareMessage()


    def __sendPrePrepareMessageToSelf(self, message):
        ''' Primary also needs the prePrepare message for subsequent validation steps '''
        key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
        self.messageLog.addToPrePrepareLog(key = key, value = message.__dict__)

    
    def __sendPrepareMessageToSelf(self, message):
        ''' node also needs its own prepare message for subsequent validation steps '''
        key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
        self.messageLog.addToPrepareLog(key = key, value = message.__dict__)
    

    def __sendCommitMessageToSelf(self, message):
        ''' node also needs its own commit message for subsequent validation steps '''
        key = self.messageLog.getPBFTMessageKey(self.pbftServiceState)
        self.messageLog.addToCommitLog(key = key, value = message.__dict__)


    # TODO: Retry until timer runs out
    async def __sendPrePrepareMessage(self, message):        
        digest = self.cryptoHelper.getDigest(json.dumps(message).encode('utf8'))
        signature = self.cryptoHelper.signPrePrepareMessage(
            phase = pbftMessage.PRE_PREPARE,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = digest
            )

        prePrepareMessage = pbftMessage.PBFTPreprepareMessage(
            phase = pbftMessage.PRE_PREPARE,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = digest,
            message = message,
            signature = signature
        )
        self.pbftServiceState.updateCurDigest(digest)
        self.__sendPrePrepareMessageToSelf(prePrepareMessage)
        await self.broadcast(prePrepareMessage)
        
          

    async def __sendPrepareMessage(self):
        signature = self.cryptoHelper.signPBFTMessage(
            phase = pbftMessage.PREPARE,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = self.pbftServiceState.curDigest,
            fromNode = self.id,
        )

        prepareMessage = pbftMessage.PBFTMessage(
            phase = pbftMessage.PREPARE,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = self.pbftServiceState.curDigest,
            fromNode = self.id,
            signature = signature,
        )

        self.__sendPrepareMessageToSelf(prepareMessage)

        await self.broadcast(prepareMessage)


    async def __sendCommitMessage(self):
        signature = self.cryptoHelper.signPBFTMessage(
            phase = pbftMessage.COMMIT,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = self.pbftServiceState.curDigest,
            fromNode = self.id,
        )

        commitMessage = pbftMessage.PBFTMessage(
            phase = pbftMessage.COMMIT,
            viewNum = self.pbftServiceState.viewNum,
            seqNum = self.pbftServiceState.seqNum,
            digest = self.pbftServiceState.curDigest,
            fromNode = self.id,
            signature = signature,
        )

        self.__sendCommitMessageToSelf(commitMessage)

        await self.broadcast(commitMessage)
    
    async def __sendResultMessage(self, prePrepareMessage, result):
        request = prePrepareMessage["message"]
        clientHost = request["clientHost"]
        clientPort = request["clientPort"]

        signature = self.cryptoHelper.signResultMessage(
            viewNum = prePrepareMessage['viewNum'],
            timestamp = request['timestamp'],
            toClientHost = clientHost,
            toClientPort = clientPort,
            fromNode = self.id,
            result = result,
        )

        resultMessage = pbftMessage.PBFTResultMessage(
            viewNum = prePrepareMessage['viewNum'],
            timestamp = request['timestamp'],
            toClientHost = clientHost,
            toClientPort = clientPort,
            fromNode = self.id,
            result = result,
            signature = signature,
        )

        await self.send(f'{clientHost}:{clientPort}', resultMessage)

    
    def __shouldAccept(self, message, prePrepareMessage):
        '''
        Messages are only accepted if a corresponding PrePrepare Message exit
        This condition is relevant for prepared and committed-local state
        '''
        predicate = (
            message['viewNum'] == prePrepareMessage['viewNum'] and 
            message['seqNum'] == prePrepareMessage['seqNum'] and 
            message['digest'] == prePrepareMessage['digest']
            )
        log.debug(f'message accepted: {predicate}')
        return predicate


    def __isPrepared(self, acceptedComs):
        ''' A request is considered prepared if
        2 f different prepare messages (including the own commit message) are in the log
        '''
        # only 2 f here since the own was already sent before this method is called
        return acceptedComs >= 2 * self.maxFaultyNodes

    
    def __isCommittedLocal(self, acceptedComs):
        ''' A node considers a request as committed if
        2 f + 1 different commit messages (including the own commit message) are in the log
        '''
        # only 2 f here since the own was already sent before this method is called
        return acceptedComs >= (2 * self.maxFaultyNodes) + 1
    

    def logCurrentState(self):
        log.debug(f'node {self.id} is primary: {self.isPrimary()}')
        log.info(f'Current view: {self.pbftServiceState.viewNum}')
        log.info(f'Current seq: {self.pbftServiceState.seqNum}')


    # -------------------------------------------------------------------------
    #   M I S C E L L A N E O U S
    # -------------------------------------------------------------------------

    def __str__(self):
        return f'''
            (
                "self.id": {self.id},
                "self.pbftServiceState": {self.pbftServiceState},
                "self.peerNodes": {self.peerNodeList},
            )
            '''
