.PHONY: build doc test clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

build:
	cd twitlib && docker build \
		--tag=twitlib ./

test: build
	docker run \
		--detach=false \
		twitlib \
		pytest /test \
		$(pyflags)

doc:
	docker run \
		-v $(shell readlink -f ./)/doc:/doc \
		-v $(shell readlink -f ./)/twitlib:/twitlib \
		nxpleuvenjenkins/doxygen \
		doxygen \
		/doc/doxygen.cfg
