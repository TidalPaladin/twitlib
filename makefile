.PHONY: build build-example doc test clean

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -wholename '*/.pytest_cache' -exec rm -rf {} +

build:
	docker build --tag=twitlib --target=base .
	docker build \
		--tag=twitlib:test \
		--build-arg cache=$(shell date +%Y-%m-%d:%H%M:%s)  \
		.

build-example: build
	docker build -t twitlib:base-example ./example/comprehensive
	docker build -t twitlib:mirror ./example/mirror

test:
	docker run -it \
		-v $(PWD)/test:/test \
		-v $(PWD)/twitlib:/twitlib \
		twitlib:test \
		--cov=/twitlib \
		${pytest_args} /test

doc:
	docker run \
		-v $(shell readlink -f ./)/doc:/doc \
		-v $(shell readlink -f ./)/twitlib:/twitlib \
		nxpleuvenjenkins/doxygen \
		doxygen \
		/doc/doxygen.cfg
