import pytest
import twitlib
import threading
import logging
import json
import os
import twitter
import requests

from threading import Thread
from queue import Queue
from twitlib.streaming import Dispatcher
from twitlib.streaming import WorkerThread
from twitlib.streaming import MirrorThread, WriterThread, MediaDownloaderThread

LOG = 'twitlib'
THREAD_WAIT = 0.1

class TestConstructors():
    """
    Trivial tests of constructor arg assignments and super() __init__ call.
    Other tests use args manually assigned by fixtures
    """

    @pytest.fixture
    def thread(self, request, mocker, worker_class):
        mocker.patch.object(threading.Thread, '__init__')
        return worker_class

    def test_Thread_init_called(self, thread, mocker):
        thread()
        Thread.__init__.assert_called_once()

    def test_Thread_init_args(self, thread, mocker):
        name = mocker.Mock(spec=str)
        daemon = mocker.Mock(spec=bool)
        thread(name=name, daemon=daemon)
        Thread.__init__.assert_called_once_with(name=name, daemon=daemon)

    arg_specs = {
        'loops' : int,
        'filters' : list,
        'dirname' : str,
        'dry_run' : bool,
        'api' : twitter.Api,
        'temp_dir' : str,
        'format' : str,
    }

    @pytest.fixture(params=arg_specs.keys())
    def mock_kwarg(self, mocker, request):
        key = request.param
        val = self.arg_specs[key]
        return key, mocker.Mock(name=key, spec=val)

    @pytest.fixture
    def has_attr(self, thread, mock_kwarg):
        worker_args = ['loops', 'filters']
        writer_args = ['dry_run', 'dirname', 'format']
        mirror_args = ['dry_run', 'api', 'temp_dir']
        downloader_args = ['dry_run', 'dirname', 'format']

        key, val = mock_kwarg
        if thread == WorkerThread:
            return key in worker_args
        elif thread == WriterThread:
            return key in writer_args
        elif thread == MirrorThread:
            return key in mirror_args
        elif thread == MediaDownloaderThread:
            return key in downloader_args
        else:
            assert(False)

    def test_attribute_set(self, thread, mock_kwarg, has_attr):
        key, val = mock_kwarg
        t = thread(**{key : val})
        assert(getattr(t, key, None) == val or not has_attr)
