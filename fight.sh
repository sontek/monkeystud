#!/bin/bash

# fight.sh -- wrapper for botfights.io <=> monkeystud
# takes a list of bots on command line

python monkeystud.py tournament 10000 $@
