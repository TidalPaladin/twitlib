.PHONY: build doc test clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

build:
	docker build \
		--file=./twitlib/Dockerfile \
		--tag=twitlib ./

test: build
	docker build \
		--file=./test/Dockerfile \
		--tag=twitlib:test ./
	docker run \
		--detach=false \
		twitlib:test \
		$(pyflags)

doc:
	docker run \
		-v $(shell readlink -f ./)/doc:/doc \
		-v $(shell readlink -f ./)/twitlib:/twitlib \
		nxpleuvenjenkins/doxygen \
		doxygen \
		/doc/doxygen.cfg
