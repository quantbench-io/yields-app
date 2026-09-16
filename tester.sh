#!/bin/sh
docker image rm -f yieldsdev:latest
docker build -t yieldsdev:latest .
docker run -it -p 8000:8000 yieldsdev:latest
