#!/bin/sh
docker image rm -f yields:latest
docker build -t yields:latest .
docker run -it -p 3000:3000 yields:latest
