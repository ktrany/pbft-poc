#! /usr/bin/env python3
import logging
import os

# create logger
class LoggerWrapper:

    def __init__(self, name, filename = './log/nodeX.log', fileMode = 'a'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(threadName)s] %(name)s %(funcName)s: \t %(message)s', "%Y-%m-%d %H:%M:%S")

        # add formatter to ch
        ch.setFormatter(formatter)

        # create dir if it does not exist yet
        logDir = os.path.dirname(filename)
        if not os.path.exists(logDir):
            os.makedirs(logDir)

        f = logging.FileHandler(filename = filename, mode = fileMode, encoding='utf-8')
        f.setLevel(logging.DEBUG)
        f.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)
        self.logger.addHandler(f)

def testLoggerOutput():
    # test logger output
    loggerW = LoggerWrapper(__name__).logger
    loggerW.debug('debug message')
    loggerW.info('info message')
    loggerW.warning('warn message')
    loggerW.error('error message')
    loggerW.critical('critical message')

# 'application' code
if __name__ == '__main__':
    testLoggerOutput()