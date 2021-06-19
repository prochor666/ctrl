#!/bin/bash

PYTHON="$(which python3)"
export PATH="$PATH:."


if [[ -x "$PYTHON" ]];
then
    $PYTHON webapp.py "$@"
else
    echo  "Python 3 is required, exiting..."
fi
