:: This file is out-of-scope for vulnerabilities. It runs the tests in docker for you.
docker run -v "%cd%:/usr/src/app" --rm -it appsecchallenge /bin/bash /usr/src/app/testapp.sh