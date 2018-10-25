FROM python:3.6.5-alpine
MAINTAINER Brian Curtich "bcurtich@gmail.com"

RUN apk update \
  && apk upgrade \
  && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app
COPY ./proxy.py .

ENTRYPOINT [ "python", "./proxy.py" ]
