#!/bin/bash
# This file is out-of-scope for vulnerabilities. PLEASE USE DOCKER K THX BYE
if [[ "$(which python)" == "/usr"* ]]; then
  source venv/bin/activate;
fi

cd memeapp

pytest --disable-warnings
