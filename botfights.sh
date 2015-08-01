#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> monkeystud

python monkeystud.py --verify=on --catch-exceptions=on --log-level=10 $@
