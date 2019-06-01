import pytest
import json
import os
from twitter import Status, User, Api
import twitter
from datetime import timedelta
import twitlib
import queue
import requests

import twitlib.util as util

from twitlib.streaming import \
    WorkerThread, \
    WriterThread, \
    MirrorThread, \
    MediaDownloaderThread, \
    Dispatcher

# See link below for full sample of Status._json dict
# https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2

@pytest.fixture
def mock_open(mocker, status):
    m = mocker.mock_open()
    mocker.patch('twitlib.streaming.open', m)
    return m

@pytest.fixture(autouse=True)
def mock_queue(mocker, status):
    m = mocker.MagicMock(spec_set=queue.Queue, name='mock_queue')
    m.get.return_value=status
    mocker.patch('queue.Queue', new=m)
    mocker.patch('twitlib.streaming.WorkerThread.QUEUE', new=m)
    mocker.patch('twitlib.streaming.WriterThread.QUEUE', new=m)
    mocker.patch('twitlib.streaming.MirrorThread.QUEUE', new=m)
    mocker.patch('twitlib.streaming.MediaDownloaderThread.QUEUE', new=m)
    return m

@pytest.fixture(params=[1, 2])
def mock_media(mocker, request):
    num_media = request.param
    class_proto = twitter.Media()

    media_list = [
            mocker.MagicMock(
                spec_set=class_proto,
                name='media%i' % i
            )
            for i in range(num_media)
    ]

    # Patch in URL for path formatting
    for i, media in enumerate(media_list):
        media.media_url_https = 'https://host.com/file{}.jpg'.format(i)

    media = mocker.MagicMock(spec_set=list, name='media')
    media.__iter__.return_value = media_list
    media.__len__.return_value = len(media_list)
    return media

@pytest.fixture
def mock_user(mocker):

    user = mocker.MagicMock(spec_set=twitter.User, name='user')

    type(user).id = mocker.PropertyMock(spec_set=int, name='user_id')
    type(user).id_str = mocker.PropertyMock(spec_set=str, name='user_id_str')
    type(user).screen_name = mocker.PropertyMock(spec_set=str, name='screen_name')

    return user

@pytest.fixture(params=[1])
def mock_mentions(mocker, request):
    num_mentions = request.param
    mentions = [
            mocker.MagicMock(
                spec_set=twitter.User,
                name='mention%i' % i
            )
            for i in range(num_mentions)
    ]

    if num_mentions:

      user_mentions = mocker.MagicMock(
              spec_set=list,
              name='user_mentions'
      )
      user_mentions.__iter__.return_value = mentions
      user_mentions.__len__.return_value = len(mentions)

    else:

      user_mentions = mocker.PropertyMock(
              name='user_mentions',
              return_value=None
      )

    return user_mentions

@pytest.fixture
def status(mocker, mock_user):
    status = mocker.MagicMock(spec_set=Status(), name='status')

    # Simple assignments
    type(status).text = mocker.PropertyMock(spec_set=str, name='text')
    type(status).full_text = mocker.PropertyMock(return_value=None)
    type(status).truncated = mocker.PropertyMock(return_value=False)
    type(status).id = mocker.PropertyMock(spec_set=int, name='id')
    type(status).id_str = mocker.PropertyMock(spec_set=str, name='id_str')
    type(status).user = mock_user

    mocker.patch.object(
            status,
            'AsDict',
            return_value=mocker.MagicMock(spec_set=dict)
    )

    return status

@pytest.fixture
def mock_worker(mocker, mock_queue):
    m = mocker.MagicMock(spec=WorkerThread, name='mock_worker')
    mocker.patch('twitlib.streaming.WorkerThread', new=m)
    return m

@pytest.fixture
def mock_writer(mocker, mock_queue):
    m = mocker.MagicMock(spec=WriterThread, name='mock_writer')
    mocker.patch('twitlib.streaming.WriterThread', new=m)
    return m

@pytest.fixture
def mock_downloader(mocker, mock_queue):
    m = mocker.MagicMock(spec=MediaDownloaderThread, name='mock_downloader')
    mocker.patch('twitlib.streaming.MediaDownloaderThread', new=m)
    return m

@pytest.fixture
def mock_mirror(mocker, mock_queue):
    m = mocker.MagicMock(spec=MirrorThread, name='mock_mirror')
    mocker.patch('twitlib.streaming.MirrorThread', new=m)
    return m

@pytest.fixture
def mock_dispatcher(mocker, mock_queue):
    m = mocker.MagicMock(spec=Dispatcher, name='mock_dispatcher')
    mocker.patch('twitlib.streaming.Dispatcher', new=m)
    return m
