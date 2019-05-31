#!python3
import os
import sys

import twitter
from twitter import Api, User, Status
from absl import app, logging
from flags import FLAGS
from logging import Formatter
from unittest import mock

from twitlib.util import *
from twitlib.streaming import Dispatcher, MirrorThread
from twitlib.filters import tweeted_by, has_hashtag

# Logging
LOG_FORMAT = '%(asctime)-s %(levelname)-1.1s %(threadName)-4.4s - %(message)s'
logging.set_verbosity(logging.INFO)
handler = logging.get_absl_handler()
formatter = Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

# Pull tokens from env vars
consumer_key = os.environ.get('TWITLIB_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITLIB_CONSUMER_SECRET')
access_token = os.environ.get('TWITLIB_ACCESS_KEY')
access_token_secret = os.environ.get('TWITLIB_ACCESS_SECRET')

api = Api(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    sleep_on_rate_limit=True,
    tweet_mode='extended',
    input_encoding='utf-32'
)

HASHTAG='DUP'
twitter_id = int(os.environ.get('TWITTER_ID', -1))


def mock_api():
    api.PostUpdate = mock.Mock(
            return_value=twitter.Status(),
            side_effect=update_side_effect
    )

def update_side_effect(*args, **kwargs):
    logging.info('PostUpdate(), called args=%s, kwargs=%s', args, kwargs)

def mirror_filters():
    return [
            MirrorThread.default_filter,
            lambda status : not status.quoted_status,
    ]

def spawn_mirror(index):
        return MirrorThread(
                api=api,
                temp_dir=os.path.join(FLAGS.dir, 'tmp'),
                dry_run=FLAGS.dry_run,
                name='MT-%i' % index,
                filters=mirror_filters()
        )

def stream(**kwargs):
    logging.info('Starting workers, dry_run=%s', FLAGS.dry_run)

    # Spin up thread pool
    threads = []
    for i in range(FLAGS.workers):
        spawn_mirror().start()

    # Connect listener to stream and filter
    listener = Dispatcher(threads=[MirrorThread])
    for line in api.GetStreamFilter(**kwargs):
        status = twitter.Status.NewFromJsonDict(line)
        if not status.id:
            logging.debug('Got empty status')
        else:
            listener.on_status(status)

def main(argv):
    del argv
    logging.info('Key: %s', api._consumer_key)
    logging.info('Auth Key: %s', api._access_token_key)
    user = api.VerifyCredentials()
    logging.info('User: %s', user.__repr__())

    if FLAGS.mock_posts:
        logging.info('Mocking API calls')
        mock_api()

    while True:
        logging.info('Starting stream')

        # Track keywords/hashtags
        if FLAGS.track:
            logging.info('track=%s', FLAGS.track)
            stream(track=FLAGS.track)

        # Follow a user ID
        elif FLAGS.follow:
            logging.info('follow=%s', FLAGS.follow)
            stream(follow=FLAGS.follow)

        # Drop to IPython REPL if no flags
        else:
            logging.info('Nothing to stream, dropping to REPL.')
            import IPython
            IPython.embed()
            sys.exit()

if __name__ == '__main__':
  app.run(main)
