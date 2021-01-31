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


parser = argparse.ArgumentParser(
    description = 'This module represents a pbft client',
    usage = '''Example:\n
    python client/index.py --path ./log/client.log --pkLoc ./keys/pairC/private_key.pem --localRepo 'D:\projects\bachelor\demo-app' --repoCloneUrl https://github.com/ktrany/pbftTestProject.git --pbftPort 10004'''
    )
parser.add_argument('--path', help = '<Required> specify the path for log output')
parser.add_argument('--pkLoc', required = True, help = '<Required> specify the location of a private key')
parser.add_argument('--localRepo', required = True, help = '<Required> specify the location of the local repository containing a dockerfile which contains the task to be executed. If the local repo does not exist, clone the project into the the given location using the specified repo clone url')
parser.add_argument('--repoCloneUrl', required = True, help = '<Required> specify the clone url of the project')
parser.add_argument('--pbftHost', default = 'localhost', help='specify the host of the pbft client')
parser.add_argument('--pbftPort', type = int, default = 8079, help='specify the port of the pbft client')
parser.add_argument('--webHookPort', type = int, default = 8080, help='specify the port the webHookListener should listen to')
args = parser.parse_args()

PATH = args.path
LOCAL_REPO = args.localRepo
REPO_CLONE_URL = args.repoCloneUrl
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
        try:
            branch = data['branch']
        except KeyError:
            return web.Response(status=400)

        log.info(f'get branch: {branch}')

        operation = Operation(REPO_CLONE_URL, branch)
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
    log.debug('args.localRepo=%s', args.localRepo)
    log.debug('args.repoCloneUrl=%s', args.repoCloneUrl)
    log.debug('args.pbftHost=%s', args.pbftHost)
    log.debug('args.pbftPort=%s', args.pbftPort)
    log.debug('args.webHookPort=%s', args.webHookPort)
    webHookListener = WebHookListener()
    webHookListener.listen(args.webHookPort)
