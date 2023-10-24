FROM python:3

# install chrome for headless testing
RUN apt-get -y update
RUN apt install -yqq \
                unzip \
                chromium \
                chromium-driver

ENV DISPLAY=:99
ENV chromedriver_path=/usr/bin/chromedriver

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/usr/src/app/testapp.sh", "novuln" ]
