#!/bin/bash

# Creates an SSH tunnel to the remote host where our old MySQL database runs.

SSH_CMD="ssh -fN -L 3307:127.0.0.1:3306 ${REMOTE_HOST_USER}@${REMOTE_HOST_NAME}"

PID=`pgrep -f "${SSH_CMD}"`
if [ $PID ] ; then
    echo $0: tunnel already running on ${PID}
else
    echo $0 launching tunnel
    $SSH_CMD
fi

