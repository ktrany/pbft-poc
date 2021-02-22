#! /usr/bin/env python3
from aiohttp import web
import argparse
import asyncio
# work around ...
# TODO: create module
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "loggerWrapper"))
from loggerWrapper import LoggerWrapper
import pbftClient
from operation import Operation
import time


parser = argparse.ArgumentParser(
    description = 'This module represents a pbft client',
    usage = '''Example:\n
    python client/index.py --path ./log/client.log --pkLoc ./keys/pairC/private_key.pem --localRepo 'D:\projects\bachelor\demo-app' --repoCloneUrl https://github.com/ktrany/pbftTestProject.git --pbftPort 10004'''
    )
parser.add_argument('--path', help = '<Required> specify the path for log output')
parser.add_argument('--pkLoc', required = True, help = '<Required> specify the location of a private key')
parser.add_argument('--pbftHost', default = 'localhost', help='specify the host of the pbft client')
parser.add_argument('--pbftPort', type = int, default = 8079, help='specify the port of the pbft client')
parser.add_argument('--webHookPort', type = int, default = 8080, help='specify the port the webHookListener should listen to')
args = parser.parse_args()

PATH = args.path + time.time().__str__()
PK_LOC = args.pkLoc
WEBHOOK_PORT = args.webHookPort

log = LoggerWrapper(__name__, PATH, 'w').logger

class WebHookListener:

    def __init__(self):
        self.pbftClient = pbftClient.PbftClient(args.pbftHost, args.pbftPort)


    async def get(self, request):
        return web.Response(text="Hello, world")


    #TODO: adjust to github/ gitlab body
    async def post(self, request):
        log.info('Hook received')
        data = await request.json()
        branch = None
        repoCloneUrl = None
        try:
            branch = data['branch']
            repoCloneUrl = data['repoCloneUrl']
        except KeyError:
            return web.Response(status=400)

        log.info(f'get branch: {branch}')

        operation = Operation(repoCloneUrl, branch)
        asyncio.ensure_future(self.pbftClient.doRequest(operation.__dict__))
        return web.Response(status=200)


    def listen(self, port = 8080):
        app = web.Application()
        app.add_routes([web.get('/', self.get)])
        app.add_routes([web.post('/webHook', self.post)])

        asyncio.ensure_future(self.pbftClient.listen())
        web.run_app(app, port = port)


if __name__ == '__main__':
    log.info('Starting application ...')
    log.debug('args.path=%s', args.path)
    log.debug('args.pkLoc=%s', args.pkLoc)
    log.debug('args.pbftHost=%s', args.pbftHost)
    log.debug('args.pbftPort=%s', args.pbftPort)
    log.debug('args.webHookPort=%s', args.webHookPort)
    webHookListener = WebHookListener()
    webHookListener.listen(args.webHookPort)
