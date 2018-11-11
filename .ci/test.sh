#!/usr/bin/env bash

NAME=$0
COMMAND=$1

function usage {
    echo "usage: $NAME <command>"
    echo
    echo "  install  Install dependencies for running test"
    echo "  run      Run tests"
    exit 1
}

if [[ "$COMMAND" == "install" ]]; then
    conda install --quiet jupyter matplotlib numpy
    pip install pytest
    pip install -e . --no-deps
elif [[ "$COMMAND" == "run" ]]; then
    pytest {{ PROJECT }} -v --duration 20
else
    if [[ -z "$COMMAND" ]]; then
        echo "Command required"
    else
        echo "Command $COMMAND not recognized"
    fi
    echo
    usage
fi
