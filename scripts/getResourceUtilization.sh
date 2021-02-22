#!/bin/bash

CPU_USAGE=$(echo | awk -v c="${cores}" -v l="${load}" '{print l*100/c}' | awk -F. '{print $1}')
MEMORY_USAGE=$(free -m | awk 'NR==2 {print $3}')

DATE=$(date "+%Y-%m-%d %H:%M")

RES_USAGE="$DATE $CPU_USAGE (($MEMORY_USAGE / 1993))"

echo $RES_USAGE >> ./output/cpu_usage.out