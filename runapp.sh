#!/bin/bash
if [[ "$(which python)" == "/usr"* ]]; then
  source venv/bin/activate;
fi
cd memeapp
if [[ $1 ]]; then
  echo "running in docker"
  flask --debug run --host=0.0.0.0
else
  echo "running on host"
  echo "PLEASE DON'T RUN THIS ON YOUR HOST OS I TOLD YOU ALREADY"
  flask --debug run
fi