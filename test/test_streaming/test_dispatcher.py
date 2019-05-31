import pytest
import logging
import json
import twitter
from twitlib.streaming import Dispatcher, WorkerThread

LOG = 'twitlib'

#######################################################################
#               DISPATCHER TESTS
#######################################################################


@pytest.mark.usefixtures('mock_queue')
class TestDispatcher():

    @pytest.fixture
    def dispatcher(self, mocker):
        w = mocker.MagicMock(spec_set=WorkerThread)
        result = Dispatcher()
        result.threads = [w]
        return result

    def test_thread_list_set(self):
        thread_arg = [WorkerThread]
        d = Dispatcher(threads=thread_arg)
        assert(d.threads == thread_arg)

    def test_enqueue_called_on_status(self, dispatcher, status):
        dispatcher.on_status(status)
        for thread in dispatcher.threads:
            thread.enqueue.assert_called_with(status)

    @pytest.mark.parametrize('call_count', [0, 1, 2])
    def test_enqueue_call_count_on_status(self, dispatcher, status, call_count):
        for i in range(call_count):
            dispatcher.on_status(status)

        for thread in dispatcher.threads:
            assert(thread.enqueue.call_count == call_count)

    @pytest.mark.parametrize('code,expected', [
        (429, False),   # Twitter rate limit code
        (1, None),
        (0, None),
    ])
    def test_on_error_return(self, dispatcher, code, expected):
        actual = dispatcher.on_error(code)
        assert(actual == expected)
