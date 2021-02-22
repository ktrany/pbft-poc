#!/bin/bash

CPU_USAGE=$(mpstat 1 1 | awk '/all/{ print 100 - $NF; exit; }')
MEMORY_USAGE=$(free -m | awk 'NR==2 {print $3}')

MEMORY_USAGE_PERCENT=`bc <<< "scale=2; $MEMORY_USAGE/1993"`

DATE=$(date "+%Y-%m-%d %H:%M")

RES_USAGE="$DATE $CPU_USAGE $MEMORY_USAGE_PERCENT"

echo $RES_USAGE >> ./output/cpu_usage.out