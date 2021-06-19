#!/bin/bash

$PYTHON="$(which python3)"

if [[ -n "$PYTHON" ]];
then
    $PYTHON webapp.py "$@"
else
    echo  "Python 3 is required, exiting..."
fi
