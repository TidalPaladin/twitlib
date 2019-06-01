import pytest
import os

from twitlib.streaming import WorkerThread, WriterThread, MirrorThread, MediaDownloaderThread
from twitlib.streaming import Dispatcher

class TestWorkerProperties():

    @pytest.fixture
    def worker(self):
        return WorkerThread()

    @pytest.mark.parametrize('val', [True, False])
    def test_dry_run(self, worker, val):
        worker.dry_run = val
        assert(worker.dry_run == val)

    def test_filters(self, worker):
        worker.filters = []
        assert(worker.filters == [])

    @pytest.mark.parametrize('val', [None, 1, 10])
    def test_loops(self, worker, val):
        worker.loops = val
        assert(worker.loops == val)

    def test_loops_validate(self, worker):
        with pytest.raises(ValueError):
            worker.loops = -1
        with pytest.raises(ValueError):
            worker.loops = 0

class TestWriterProperties(TestWorkerProperties):

    @pytest.fixture
    def worker(self):
        return WriterThread()

    def test_dirname(self, worker):
        worker.dirname = 'dir'
        assert(worker.dirname == 'dir')

    def test_format(self, worker):
        worker.format = 'format_str'
        assert(worker.format == 'format_str')

class TestMediaDownloaderProperties(TestWorkerProperties):

    @pytest.fixture
    def worker(self):
        return MediaDownloaderThread()

    def test_dirname(self, worker):
        worker.dirname = 'dir'
        assert(worker.dirname == 'dir')

    def test_format(self, worker):
        worker.format = 'format_str'
        assert(worker.format == 'format_str')

class TestMirrorProperties(TestWorkerProperties):

    @pytest.fixture
    def worker(self):
        return MirrorThread()

    def test_temp_dir(self, worker):
        worker.temp_dir = 'dir'
        assert(worker.temp_dir == 'dir')

    def test_api(self, api, worker):
        worker.api = api
        assert(worker.api == api)

class TestDispatcherProperties():

    @pytest.fixture
    def dispatcher(self):
        return Dispatcher()

    @pytest.fixture(params=[
        [WorkerThread],
        [WorkerThread, WriterThread]
    ])
    def threads(self, request):
        return request.param

    def test_threads(self, dispatcher, threads):
        dispatcher.threads = threads
        assert(dispatcher.threads == threads)

