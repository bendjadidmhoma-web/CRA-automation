FROM n8nio/n8n:latest

USER root

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install pymupdf --break-system-packages

WORKDIR /data

COPY . /data

USER node