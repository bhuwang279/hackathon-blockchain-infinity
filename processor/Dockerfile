FROM ubuntu:bionic

RUN \
 apt-get update \
 && apt-get install -y -q curl gnupg \
 && curl -sSL 'http://p80.pool.sks-keyservers.net/pks/lookup?op=get&search=0x8AA7AF1F1091A5FD' | apt-key add -  \
 && echo 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' >> /etc/apt/sources.list \
 && apt-get update

RUN apt-get install -y -q python3-sawtooth-sdk

WORKDIR /project/sawtooth-infinity


ENV PATH $PATH:/project/sawtooth-infinity/bin

CMD ['tp-infinity']
