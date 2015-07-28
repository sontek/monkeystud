#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> monkeystud
# either verify a bot, or
# run a botfight

if [ $1 = 'verify' ];
    then
    python monkeystud.py verify $2
elif [ $1 = 'fight' ];
    then
    shift
    python monkeystud.py tournament 1000 $@
fi
