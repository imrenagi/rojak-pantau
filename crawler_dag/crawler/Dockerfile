FROM ubuntu:16.04

MAINTAINER Imre Nagi <imre.nagi2812@gmail.com>

RUN apt-get update
RUN apt-get install -y build-essential \
  libffi-dev \
  libssl-dev \
  libxml2-dev \
  libxslt-dev  \
  python-pip \
  python \
  python-dev \
  python-setuptools \
  libmysqlclient-dev

RUN pip install virtualenv
RUN virtualenv scrapy
RUN /bin/bash -c "source scrapy/bin/activate"

ADD . /src
WORKDIR /src

VOLUME /src

ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

CMD [ "python" ]
