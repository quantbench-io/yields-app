#!/bin/sh
docker image rm -f yieldsback:latest
docker build -t yieldsback:latest .
docker run -it -p 5179:3000 yieldsback:latest