#!python3
import os
import sys

import twitter
from twitter import Api, User, Status
from unittest import mock
from absl import app, logging
from flags import FLAGS
from logging import Formatter

from twitlib.util import *
from twitlib.streaming import WriterThread, Dispatcher, MirrorThread, MediaDownloaderThread
from twitlib.filters import is_rt_game, tweeted_by, has_hashtag
from get_access_token import get_access_token


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

twitter_id = os.environ.get('TWITTER_ID', None)

def mock_api():
    """
    Mocks PostUpdate so no posts are sent to Twitter. Will print
    log messages with args/kwargs when PostUpdate is called
    """

    def update_side_effect(*args, **kwargs):
        logging.info('PostUpdate(), called args=%s, kwargs=%s', args, kwargs)

    api.PostUpdate = mock.Mock(
            return_value=twitter.Status(),
            side_effect=update_side_effect
    )

def mirror_filters():
    return [
            MirrorThread.default_filter,
            lambda status : not status.quoted_status,
    ]

def spawn_writer(index):
        return WriterThread(
                dirname=FLAGS.dir,
                dry_run=FLAGS.dry_run,
                format=FLAGS.write_format,
                name='WT-%i' % index
        )

def spawn_downloader(index):
        return MediaDownloaderThread(
                dirname=FLAGS.dir,
                dry_run=FLAGS.dry_run,
                format=FLAGS.media_format,
                name='DT-%i' % index
        )

def spawn_mirror(index):
        return MirrorThread(
                api=api,
                temp_dir=os.path.join(FLAGS.dir, 'tmp'),
                dry_run=FLAGS.dry_run,
                name='MT-%i' % index,
                filters=mirror_filters()
        )

def get_dispatcher():
    threads = []
    if FLAGS.download:
        threads.append(MediaDownloaderThread)
    if FLAGS.mirror:
        threads.append(MirrorThread)
    if FLAGS.writer:
        threads.append(WriterThread)
    return Dispatcher(threads=threads)

def stream(**kwargs):
    logging.info('Starting workers, dry_run=%s', FLAGS.dry_run)

    # Spin up thread pool
    threads = []
    for i in range(FLAGS.workers):
        if FLAGS.download:
            spawn_downloader().start()
        if FLAGS.mirror:
            spawn_mirror().start()
        if FLAGS.writer:
            spawn_writer().start()

    # Connect listener to stream and filter
    listener = get_dispatcher()
    for line in api.GetStreamFilter(**kwargs):
        status = twitter.Status.NewFromJsonDict(line)
        if not status.id:
            logging.debug('Got empty status')
        else:
            listener.on_status(status)

def main(argv):
    del argv

    if FLAGS.auth:
        logging.info('Starting authentication flow')
        get_access_token(consumer_key, consumer_secret)
        logging.info('Authentication done, exiting...')
        sys.exit()

    logging.info('Key: %s', api._consumer_key)
    logging.info('Auth Key: %s', api._access_token_key)

    user = api.VerifyCredentials()
    logging.info('User: %s', user.__repr__())


    if FLAGS.mock_posts:
        logging.info('Mocking API calls')
        mock_api()

    while True:
        logging.info('Starting stream')
        if FLAGS.track:
            logging.info('track=%s', FLAGS.track)
            stream(track=FLAGS.track)
        elif FLAGS.follow:
            logging.info('follow=%s', FLAGS.follow)
            stream(follow=FLAGS.follow)
        else:
            logging.error('Nothing to stream, exiting...')
            return

if __name__ == '__main__':
  app.run(main)
