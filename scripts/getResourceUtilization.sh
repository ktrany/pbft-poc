#!/bin/bash

CPU_USAGE=$(top -b -n2 -p 1 | fgrep "Cpu(s)" | tail -1 | awk -F'id,' -v prefix="$prefix" '{ split($1, vs, ","); v=vs[length(vs)]; sub("%", "", v); printf "%s%.1f%%\n", prefix, 100 - v }')
MEMORY_USAGE=$(free -m | awk 'NR==2 {print $3}')

DATE=$(date "+%Y-%m-%d %H:%M")

RES_USAGE="$DATE $CPU_USAGE (($MEMORY_USAGE / 1993))"

echo $RES_USAGE >> ./output/cpu_usage.out