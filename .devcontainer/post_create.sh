#!/bin/bash

# this project needs these pakcages to work
# sudo apt update && sudo apt install -y --no-install-recommends redis

rye sync
rye run pre-commit install
