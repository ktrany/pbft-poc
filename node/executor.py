#! /usr/bin/env python3
import index
from loggerWrapper import LoggerWrapper
import subprocess

log = LoggerWrapper(__name__, index.PATH).logger

class Executor:

    def __init__(self):
        pass

    def runTask(self, dockerFileLoc, imageTag, port):
        buildProcess = subprocess.run(['docker', 'build', '-t', imageTag, dockerFileLoc], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                universal_newlines=True)

        if buildProcess.returncode != 0:
            errMessage = f'Task: Build image failed. ErrCode={buildProcess.returncode}'
            log.debug(errMessage)
            return errMessage
        
        log.debug(f'Task: Build image completed. StatCode={buildProcess.returncode}')

        taskProcess = subprocess.run(['docker', 'run', '--rm', '-p', port, imageTag], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                universal_newlines=True)
        log.debug(f'Task: Execution completed. StatCode={taskProcess.returncode}')

        # delete image for next run
        deleteTask = subprocess.run(['docker', 'rmi', imageTag], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                universal_newlines=True)
        log.debug(f'Task: Delete image completed. StatCode={deleteTask.returncode}')

        return taskProcess