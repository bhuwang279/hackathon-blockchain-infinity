FROM ubuntu:bionic

RUN \
 apt-get update \
 && apt-get install -y -q curl gnupg \
 && curl -sSL 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add -  \
 && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
 && apt-get update

RUN apt-get install -y --allow-unauthenticated -q \
    curl \
    python3-pip \
    python3-sawtooth-cli \
    python3-sawtooth-sdk \
    python3-sawtooth-rest-api

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs npm

RUN pip3 install \
    aiohttp \
    aiopg \
    bcrypt \
    grpcio-tools \
    itsdangerous \
    nose2 \
    psycopg2-binary \
    pycrypto \
    pylint \
    pycodestyle

WORKDIR /project/sawtooth-infinity


ENV PATH $PATH:/project/sawtooth-infinity/bin
