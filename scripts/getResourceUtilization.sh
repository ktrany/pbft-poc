#!/bin/bash

CPU_USAGE=$(LC_ALL=C top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEMORY_USAGE=$(free -m | awk 'NR==2 {print $3}')

DATE=$(date "+%Y-%m-%d %H:%M")

RES_USAGE="$DATE $CPU_USAGE $(($MEMORY_USAGE / 1993))"

echo $RES_USAGE >> ./output/cpu_usage.out