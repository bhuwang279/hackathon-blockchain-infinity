

FROM ubuntu:bionic

RUN \
 apt-get update \
 && apt-get install -y -q curl gnupg \
 && curl -sSL 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add -  \
 && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
 && apt-get update

RUN apt-get install -y --allow-unauthenticated -q python3-grpcio-tools \
    python3-pip \
    python3-sawtooth-rest-api \
    python3-sawtooth-sdk

RUN pip3 install \
    aiohttp \
    aiopg \
    bcrypt \
    itsdangerous \
    pycrypto \
    psycopg2-binary


WORKDIR /project/sawtooth-infinity

ENV PATH $PATH:/project/sawtooth-infinity/bin

EXPOSE 8000/tcp

CMD ['infinity-rest-api']
