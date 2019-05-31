FROM python:3.7-slim-stretch as base
RUN pip install --user --no-cache-dir python-twitter
COPY twitlib /twitlib

FROM base as test
ARG cache=1
COPY test /test
RUN mkdir -p /cov
RUN pip install --no-cache-dir \
	pytest \
	pytest-cov \
	pytest-mock \
	pytest-timeout
ENTRYPOINT [ "pytest" ]
CMD [ "--cov=/twitlib", "--cov-report=xml:/cov/coverage.xml", "--cov-report=term", "/test"]
