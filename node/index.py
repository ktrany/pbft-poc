#! /usr/bin/env python3
import argparse
import asyncio
# work around ...
# TODO: create module
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "loggerWrapper"))
from loggerWrapper import LoggerWrapper
import pbftNode
import time

parser = argparse.ArgumentParser(description='This module represents a Replica (either Backup or Primary) according to PBFT')
parser.add_argument('--id', required = True, type = int, help='<Required> specify the id of the service. Integer in set { 0, ..., |R| - 1 } expected with |R| as total number of replicas')
parser.add_argument('--peerNodeAddrList', required = True, nargs = '+', help = '<Required> specify the address YOUR_HOST:YOUR_PORT of one peer node. Can take multiple inputs separated by whitespace')
parser.add_argument('--path', required = True, help = '<Required> specify the path for log output')
parser.add_argument('--pkLoc', required = True, help = '<Required> specify the location of a private key')
parser.add_argument('--host', default = 'localhost', help='specify the host of the service')
parser.add_argument('--port', type = int, default = 8080, help='specify the port of the service')
args = parser.parse_args()

ID = args.id
PORT = args.port
PATH = args.path + time.time().__str__()
PK_LOC = args.pkLoc
log = LoggerWrapper(__name__, PATH, 'w').logger

async def main():
    log.info('Starting application ...')
    log.debug('args.id=%s', args.id)
    log.debug('args.peerNodeAddrList=%s', args.peerNodeAddrList)
    log.debug('args.path=%s', args.path)
    log.debug('args.pkLoc=%s', args.pkLoc)
    log.debug('args.host=%s', args.host)
    log.debug('args.port=%s', args.port)

    node = pbftNode.PBFTNode(id = args.id, host = args.host, port = args.port, peerNodeList = args.peerNodeAddrList)
    log.debug('node=%s', node)

    asyncio.ensure_future(node.doOnePbftRound())

    await node.listen()
    log.info('Application closed ...')


if __name__ == '__main__':
    asyncio.run(main())