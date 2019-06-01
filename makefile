.PHONY: build build-example doc test clean

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -wholename '*/.pytest_cache' -exec rm -rf {} +

build:
	docker build --tag=twitlib --target=base .

build-example: build
	docker build -t twitlib:base-example ./example/comprehensive
	docker build -t twitlib:mirror ./example/mirror

test: build
	docker build --tag=twitlib:test .
	docker run -it twitlib:test \

doc:
	docker run \
		-v $(shell readlink -f ./)/doc:/doc \
		-v $(shell readlink -f ./)/twitlib:/twitlib \
		nxpleuvenjenkins/doxygen \
		doxygen \
		/doc/doxygen.cfg
