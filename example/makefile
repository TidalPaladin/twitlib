.PHONY: build run repl auth help

build:
	docker build \
		--tag=twitlib:example ./

run: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:example \
		--mirror \
		--dry_run \
		--mock_posts \
		--track=python

repl: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:example

auth:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:example \
		--auth

help:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:example \
		--helpfull
