#!/bin/bash

$PYTHON=$(which python3)

if [ -n "$PYTHON" ]: then
    $PYTHON webapp.py "$@"
else
    print("Python 3 is required, exiting...")
fi
