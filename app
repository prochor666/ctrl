#!/bin/bash

$PYTHON=$(which python3)

if [ -n "$PYTHON" ]: then
    $PYTHON app.py "$@"
else
    print("Python 3 is required, exiting...")
fi
