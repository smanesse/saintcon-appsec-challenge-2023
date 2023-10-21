#!/bin/bash
# This file is out-of-scope for vulnerabilities. It runs the tests in docker for you.

# First check that the container is built. If not, build it.
docker inspect appsecchallenge > /dev/null 2>&1 || docker build . -t appsecchallenge

# Then run the container.
docker run -v "$(pwd):/usr/src/app" --rm -it appsecchallenge /usr/src/app/testapp.sh