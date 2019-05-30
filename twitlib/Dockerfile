FROM python:3.7-slim-stretch
RUN mkdir -p /twitlib
ADD ./*.py /twitlib/
ADD ./test /test
RUN pip install python-twitter pytest pytest-mock pytest-timeout
