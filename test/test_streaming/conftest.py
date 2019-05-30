import pytest
import json
import os
from twitter import Status, User
from datetime import timedelta
import twitlib
import queue
import twitter
import requests

from twitlib.streaming import Dispatcher
from twitlib.streaming import WorkerThread, WriterThread, MirrorThread, MediaDownloaderThread
import twitlib.util as util

# See link below for full sample of Status._json dict
# https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2

#######################################################################
#               WORKER THREAD OBJECTS
#######################################################################

@pytest.fixture
def mock_args(dirname, api, mocker):
    mock_args = {
        'loops' : 2,
        'filters' : [lambda s : True],
        'dirname' : dirname,
        'dry_run' : False,
        'api' : api,
        'temp_dir' : 'temp'+dirname,
        'format' : 'status_%(id)s.json',
    }
    for k, v in mock_args.items():
        mock_args[k] = mocker.PropertyMock(return_value=v)
    return mock_args

@pytest.fixture(params=[
    WorkerThread,
    WriterThread,
    MirrorThread,
    MediaDownloaderThread
])
def worker_class(request):
    return request.param

@pytest.fixture(params=[
    WriterThread,
    MirrorThread,
    MediaDownloaderThread
])
def worker_subclass(request):
    return request.param

@pytest.fixture
def base_worker(mock_args):
    result = WorkerThread()
    for k, v in mock_args.items():
        setattr(type(result), k, v)
    return result

@pytest.fixture
def worker(mocker, worker_class, mock_args):
    result = worker_class()
    for k, v in mock_args.items():
        setattr(type(result), k, v)
    return result

@pytest.fixture
def subworker(mocker, worker_subclass, mock_args):
    result = worker_subclass()
    for k, v in mock_args.items():
        setattr(type(result), k, v)
    return result

@pytest.fixture
def static_func(subworker, worker_subclass):
    """
    Map a worker class to list of functions to not be called if
    validate_status() == False
    """
    if worker_subclass == MirrorThread:
        return subworker.mirror
    elif worker_subclass == WriterThread:
        return subworker.write_status
    elif worker_subclass == MediaDownloaderThread:
        return subworker.download_media
    else:
        assert(False)

@pytest.fixture
def call(mocker, status, subworker, worker_subclass):
    filename = WorkerThread.format_filename.return_value
    if worker_subclass == WriterThread:
        return mocker.call(status, filename)
    elif worker_subclass == MirrorThread:
        return mocker.call(subworker.api, status, subworker.temp_dir)
    elif worker_subclass == MediaDownloaderThread:
        return mocker.call(status, filename)
    else:
        assert(False)

#######################################################################
#               PARAMETRIZED FILE PATHS
#######################################################################

@pytest.fixture( params=[
    'status_%(id)s.json',
    'status_%(text)s.json',
    '%(created_at)s.json'
])
def format(request):
    return request.param

@pytest.fixture
def dirname():
    return 'testdir'


#######################################################################
#               PATCHES
#######################################################################

@pytest.fixture
def validate_true(mocker):
    mocker.patch.object(WorkerThread, 'validate_status', return_value=True)

@pytest.fixture
def validate_false(mocker):
    mocker.patch.object(WorkerThread, 'validate_status', return_value=False)

@pytest.fixture
def patch_statics(patch_mirror, patch_write, patch_download, patch_format):
    pass

@pytest.fixture
def patch_remove_urls(mocker, status):
    mocker.patch.object(twitlib.util, 'remove_urls', return_value=status.text)

@pytest.fixture
def patch_mirror(mocker, api):
    mocker.patch.object(
            MirrorThread,
            'mirror',
            return_value=api.PostUpdate(),
            side_effect=api.PostUpdate,
            spec=MirrorThread.mirror
    )

@pytest.fixture
def patch_write(mocker):
    mocker.patch.object(
            WriterThread,
            'write_status',
            return_value=mocker.MagicMock(name='write_status', spec=str),
            spec=WriterThread.write_status
    )

@pytest.fixture
def patch_download(mocker):
    mocker.patch.object(
            MediaDownloaderThread,
            'download_media',
            return_value=mocker.MagicMock(name='download_media', spec=list),
            spec=MediaDownloaderThread.download_media
    )

@pytest.fixture
def patch_format(mocker):
    mocker.patch.object(
            WorkerThread,
            'format_filename',
            return_value=mocker.MagicMock(name='format_filename', spec=str),
            spec=WorkerThread.format_filename
    )

@pytest.fixture
def patch_display_text(mocker, inject_display_text):
    mocker.patch.object(
            util,
            'display_text',
            return_value=display_text,
            spec=util.display_text
    )
