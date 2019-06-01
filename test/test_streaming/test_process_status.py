import pytest
import twitter
from twitlib.streaming import WorkerThread, MirrorThread, WriterThread, MediaDownloaderThread

@pytest.mark.usefixtures('patch_statics')
class TestProcessStatus():
    """Parameterized to test all worker classes"""

    @pytest.mark.usefixtures('validate_true')
    def test_static_call(self, subworker, status, static_func):
        subworker.process_status(status)
        static_func.assert_called_once()

    @pytest.mark.usefixtures('validate_true')
    def test_static_call_args(self, status, subworker, static_func, call):
        """Tests process_status() mirrors tweet"""
        subworker.process_status(status)
        assert(call in static_func.call_args_list)

    @pytest.mark.usefixtures('validate_true')
    def test_return(self, subworker, status, static_func):
        """Tests process_status() returns list of written files"""
        expected = static_func.return_value
        actual = subworker.process_status(status)
        assert(expected == actual)

    @pytest.mark.usefixtures('validate_false')
    def test_noop_on_validate_fail(self, subworker, status, static_func):
        subworker.process_status(status)
        static_func.assert_not_called()


@pytest.mark.usefixtures("validate_true", 'dry_run', 'patch_statics')
class TestDryRun():
    """Parameterized to test all worker classes"""

    @pytest.fixture
    def dry_run(self, mocker, subworker):
        subworker.dry_run = True

    def test_dry_run_respected(self, subworker, status, static_func):
        assert(subworker.dry_run)
        subworker.process_status(status)
        static_func.assert_not_called()

    def test_dry_run_return(self, subworker, status, static_func):
        assert(subworker.dry_run)
        expected = None
        actual = subworker.process_status(status)
        assert(expected == actual)

@pytest.mark.usefixtures('patch_format')
class TestWrite():

    @pytest.fixture
    def thread(self):
        return WriterThread()

    @pytest.mark.usefixtures('validate_true')
    def test_calls_format(self, thread, status):
        thread.process_status(status)
        thread.format_filename.assert_called_once_with(status, thread.format, thread.dirname)

@pytest.mark.usefixtures('patch_format')
class TestDownload():

    @pytest.fixture
    def thread(self):
        return MediaDownloaderThread()

    @pytest.mark.usefixtures('validate_true')
    def test_calls_format(self, thread, status):
        thread.process_status(status)
        thread.format_filename.assert_called_once_with(status, thread.format, thread.dirname)
