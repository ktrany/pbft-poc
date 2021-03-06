#! /usr/bin/env python3
import index
from loggerWrapper import LoggerWrapper
import subprocess
import time

log = LoggerWrapper(__name__, index.PATH).logger

class Executor:

    def __init__(self):
        pass

    def runTask(self, repoCloneUrl, targetBranch, imageTag):
        start = time.perf_counter()
        buildProcess = subprocess.run(['docker', 'build', '-t', imageTag, f'{repoCloneUrl}#{targetBranch}'], capture_output=True, encoding='utf-8')

        if buildProcess.returncode != 0:
            errMessage = f'Task: Build image failed. ErrCode={buildProcess.returncode}'
            log.debug(errMessage)
            return buildProcess
        
        log.debug(f'Task: Build image completed. StatCode={buildProcess.returncode}')

        taskProcess = subprocess.run(['docker', 'run', '--cap-add=SYS_ADMIN', '--rm', imageTag], capture_output=True, encoding='utf-8')
        log.debug(f'Task: Execution completed. StatCode={taskProcess.returncode}')

        # delete image for next run
        deleteTask = subprocess.run(['docker', 'rmi', imageTag], capture_output=True, encoding='utf-8')
        log.debug(f'Task: Delete image completed. StatCode={deleteTask.returncode}')

        log.info(f'result: {taskProcess}')

        end = time.perf_counter()
        log.info(f'Task execution time: {end - start}s')

        return taskProcess