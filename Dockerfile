FROM python:3

# install chrome for headless testing
RUN apt-get -y update
RUN apt install -yqq \
                unzip
ARG CHROME_VERSION="114.0.5735.198-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
  && apt install -y /tmp/chrome.deb \
  && rm /tmp/chrome.deb
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99
ENV chromedriver_path=/usr/local/bin/chromedriver

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/usr/src/app/testapp.sh", "novuln" ]
