FROM python:3.7-slim-stretch

COPY test /test
COPY twitlib /twitlib

RUN pip install python-twitter pytest pytest-mock pytest-timeout

ENTRYPOINT [ "pytest", "/test" ]
