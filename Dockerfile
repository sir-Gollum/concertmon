FROM python:3.9-alpine

COPY requirements.txt /

RUN apk add --update --no-cache curl g++ gcc libxslt-dev && \
    python3 -m pip install -r /requirements.txt