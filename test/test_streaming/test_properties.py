import pytest
import os
from twitlib.streaming import Dispatcher
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

