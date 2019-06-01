import pytest
import os

from queue import Queue
from twitlib.streaming import WorkerThread

THREAD_WAIT = 0.1

class TestWorker():
    """Parameterized to test all worker classes"""

    def test_daemon_default(self, worker):
        assert(worker.daemon)

    @pytest.mark.timeout(THREAD_WAIT, method='signal')
    def test_kill_no_process(self, worker, mocker):
        mocker.patch.object(WorkerThread, 'dequeue', return_value=None)
        mocker.patch.object(worker, 'process_status')
        worker.run()

        WorkerThread.dequeue.assert_called_once()
        worker.process_status.assert_not_called()

    @pytest.fixture
    def output_file(self):
        return 'out_file.json'

    @pytest.fixture
    def mock_format(self, mocker, output_file):
        mock_fmt = mocker.MagicMock(spec_set=str, name='thread.format')
        mock_fmt.format.return_value = output_file
        return mock_fmt

    def test_calls_format_mock(self, status, output_file, dirname, mock_format):
        WorkerThread.format_filename(status, mock_format, dirname)
        kwargs = status.AsDict()
        mock_format.format.assert_called_once_with(**kwargs)

    def test_calls_format_stub(self, status, output_file, dirname, mock_format, mocker):
        kwargs = {'id' : 0, 'val': 1}
        mocker.patch.object(status, 'AsDict', return_value=kwargs)
        WorkerThread.format_filename(status, mock_format, dirname)
        mock_format.format.assert_called_once_with(**kwargs)

    def test_default_filter_returns_true(self, status):
        filter_ret = WorkerThread.default_filter(status)
        assert(filter_ret == True)


@pytest.mark.timeout(THREAD_WAIT, method='signal')
class TestQueue():
    """Parameterized to test all worker classes"""

    def test_enqueue_call_count(self, worker_class, status, mock_queue):
        worker_class.enqueue(status)
        mock_queue.put.assert_called_once()

    def test_enqueue_call_args(self, worker_class, status, mock_queue):
        worker_class.enqueue(status)
        mock_queue.put.assert_called_once_with(status, block=True, timeout=None)

    def test_dequeue_call_count(mocker, worker_class, status, mock_queue):
        worker_class.dequeue()
        mock_queue.get.assert_called_once_with(block=True, timeout=None)

    def test_dequeue_value(mocker, worker_class, status):
        item = worker_class.dequeue()
        assert(item == status)

@pytest.mark.usefixtures('dequeue_once')
class TestExceptions():

    @pytest.fixture
    def dequeue_once(self, mock_queue):
        def side_effect():
            mock_queue.get.return_value=None
        mock_queue.task_done.side_effect=side_effect

    @pytest.fixture(params=[KeyboardInterrupt, SystemExit])
    def unhandled_exception(self, mocker, worker, request):
        mocker.patch.object(worker, 'process_status', side_effect=request.param)
        return request.param

    def test_process_call_raises(self, base_worker, status):
        with pytest.raises(NotImplementedError):
            base_worker.process_status(status)

    @pytest.mark.timeout(THREAD_WAIT, method='signal')
    def test_unhandled_exception(self, worker, unhandled_exception):
        """Test exceptions that should not be caught by WorkerThread.run()"""
        with pytest.raises(unhandled_exception):
            worker.run()
