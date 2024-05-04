#!/usr/bin/env bash

pip3 list | grep -q openai || {
    pip3 -qq install openai
}

pip3 list | grep -q requests || {
    pip3 -qq install requests
}

pip3 list | grep -q dotenv || {
    pip3 -qq install python-dotenv
}

/app/cli.py $@
