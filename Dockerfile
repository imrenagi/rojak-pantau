FROM ubuntu:14.04

MAINTAINER Imre Nagi <imre.nagi2812@gmail.com>

RUN sudo apt-get update
RUN sudo apt-get install -y build-essential python python-dev python-setuptools
RUN sudo apt-get install -y libffi-dev libssl-dev libxml2-dev libxslt-dev  python-pip
RUN sudo apt-get install -y libmysqlclient-dev

ADD . /src
WORKDIR /src

ADD requirements.txt /src/requirements.txt
RUN pip install -r /src/requirements.txt

CMD [ "python" ]
