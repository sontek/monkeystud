#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> monkeystud

monkeystud --catch-exceptions=true --log-level=INFO tournament $@
