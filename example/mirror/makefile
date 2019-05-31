.PHONY: build run repl auth help

build:
	docker build \
		--tag=twitlib:mirror ./

run: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:mirror \
		--mirror \
		--dry_run \
		--mock_posts \
		--track=python

repl: build
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:mirror

auth:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:mirror \
		--auth

help:
	docker run \
		--detach=false \
		--env-file=secrets.env \
		twitlib:mirror \
		--helpfull
