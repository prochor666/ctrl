#!/bin/bash

PYTHON="$(which python3)"

if [[ -x "$PYTHON" ]];
then
    $PYTHON webapp.py "$@"
else
    echo  "Python 3 is required, exiting..."
fi
