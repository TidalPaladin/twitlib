# Basic Example

A sample script with argument parsing is provided here, along with
Dockerfiles for containerization. By default it will stream tweets
with "#python" and simulate mirroring of these tweets via a
`--dry_run` flag.

## Usage

### Setting Environment Variables
In order to function the script requires tokens for your twitter app
and the twitter account for which the app has been authorized. If you
have not generated access tokens for an account, the
`get_access_token.py` file provides some helper functions.

If running with Docker, a skeleton `secrets.env` file is provided
which you can update with the tokens for your app. Otherwise, set the
environment variables in your preferred way before running the script.

```sh
# Key/secret for your app
TWITLIB_CONSUMER_KEY=key
TWITLIB_CONSUMER_SECRET=secret

# Authorization key/secret for the twitter account
TWITLIB_ACCESS_KEY=key
TWITLIB_ACCESS_SECRET=secret

# Fallback to streaming tweets from this ID if no
# overriding args are supplied
TWITTER_ID=1234

# If saving tweets/media, write to this directory
TWITLIB_DIR=/path/to/dir
```

### Flags

Various command line flags are provided in `flags.py`.
