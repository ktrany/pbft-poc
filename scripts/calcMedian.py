#! /usr/bin/env python
import os
import statistics
directory = 'log'

taskExecTimeWithDockerList = []
taskExecTimeWithoutDockerList = []
timeReqAcceptedList = []

def retrieveResults(file):
    with open(file, "r", encoding='utf-8') as f:
        Lines = f.readlines()
        count = 0
        # Strips the newline character
        for line in Lines:
            count += 1
            if 'Task execution time:' in line:
                words = line.split()
                time = words[-1][:-1]
                print(time)
                taskExecTimeWithDockerList.append(float(time))

            if 'Time Req accepted' in line:
                words = line.split()
                time = words[-1][:-1]
                print(time)
                timeReqAcceptedList.append(float(time))
            
            if 'self.result' in line:
                # omit this part: '\nRan all test suites.\n'
                words = line[:-27].split()
                time = words[-1][:-1]
                print(time)
                taskExecTimeWithoutDockerList.append(float(time))
                return

for filename in os.listdir(directory):
    filePath = os.path.join(directory, filename)
    print(filePath)
    retrieveResults(filePath)

print(taskExecTimeWithDockerList)
print(taskExecTimeWithoutDockerList)
print(timeReqAcceptedList)

print(f'taskExecTimeWithDockerList: {statistics.median(taskExecTimeWithDockerList)}')
print(f'taskExecTimeWithoutDockerList: {statistics.median(taskExecTimeWithoutDockerList)}')
print(f'timeReqAcceptedList: {statistics.median(timeReqAcceptedList)}')
