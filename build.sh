#!/bin/sh -e

docker build . -t registry1.ctdn.net/library/barcode-web-api:latest

docker push registry1.ctdn.net/library/barcode-web-api:latest
