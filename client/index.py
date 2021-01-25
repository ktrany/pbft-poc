#! /usr/bin/env python3
# import aiohttp
import argparse
import asyncio
# work around ...
# TODO: create module
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "loggerWrapper"))
from loggerWrapper import LoggerWrapper
import pbftClient

parser = argparse.ArgumentParser(description='This module represents a pbft client')
parser.add_argument('--path', help = '<Required> specify the path for log output')
parser.add_argument('--pkLoc', required = True, help = '<Required> specify the location of a private key')
parser.add_argument('--pbftHost', default = 'localhost', help='specify the host of the client')
parser.add_argument('--pbftPort', type = int, default = 8079, help='specify the port of the client')
args = parser.parse_args()

PATH = args.path
PK_LOC = args.pkLoc
log = LoggerWrapper(__name__, PATH, 'w').logger

async def main():
    log.info('Starting application ...')
    log.debug('args.path=%s', args.path)
    log.debug('args.pkLoc=%s', args.pkLoc)
    log.debug('args.pbftHost=%s', args.pbftHost)
    log.debug('args.pbftPort=%s', args.pbftPort)

    client = pbftClient.PbftClient(args.pbftHost, args.pbftPort)
    log.debug('client=%s', client)

    asyncio.ensure_future(client.doRequest())

    await client.listen()
    log.info('Application closed ...')

if __name__ == '__main__':
    asyncio.run(main())
