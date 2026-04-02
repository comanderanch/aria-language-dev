#!/bin/bash

LOG_DIR="$(pwd)/aria-exp/system"
MASTER="$LOG_DIR/master.log"
FAIL="$LOG_DIR/fail.log"

mkdir -p "$LOG_DIR"

TS=$(date +"%Y-%m-%d %H:%M:%S")

TYPE=$1
MESSAGE=$2

if [ "$TYPE" == "FAIL" ]; then
    echo "[$TS] FAIL: $MESSAGE" >> "$FAIL"
fi

echo "[$TS] $TYPE: $MESSAGE" >> "$MASTER"

echo "LOGGED: $TYPE"
