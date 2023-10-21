#!/bin/bash

# Create the docker image if it doesn't exist
docker inspect appsecchallenge > /dev/null 2>&1 || docker build . -t appsecchallenge

# Run it
docker run -v "$(pwd):/usr/src/app" -p 127.0.0.1:5000:5000 -it --rm appsecchallenge /usr/src/app/runapp.sh 1