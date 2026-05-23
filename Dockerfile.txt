FROM n8nio/n8n:latest

USER root

RUN apk add --no-cache python3 py3-pip
RUN pip3 install pymupdf

WORKDIR /data

COPY . /data

USER node