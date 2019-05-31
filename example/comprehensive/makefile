.PHONY: build run repl auth help

build:
	docker build \
		--tag=twitlib:base-example ./

run: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:base-example \
		--mirror \
		--dry_run \
		--mock_posts \
		--track=python

repl: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:base-example

auth:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:base-example \
		--auth

help:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:base-example \
		--helpfull
