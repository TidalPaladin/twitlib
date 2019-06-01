.PHONY: build build-example doc test clean

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -wholename '*/.pytest_cache' -exec rm --force {} +

build:
	docker build --tag=twitlib ./twitlib

build-example: build
	docker build -t twitlib:base-example ./example/comprehensive
	docker build -t twitlib:mirror ./example/mirror

test: build
	docker build --tag=twitlib:test ./test
	docker run -it twitlib:test \
		--cov=/twitlib \
		$(pyflags) \
		/test

doc:
	docker run \
		-v $(shell readlink -f ./)/doc:/doc \
		-v $(shell readlink -f ./)/twitlib:/twitlib \
		nxpleuvenjenkins/doxygen \
		doxygen \
		/doc/doxygen.cfg
