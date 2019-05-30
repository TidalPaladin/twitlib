import pytest
from twitlib.streaming import WorkerThread
from twitlib.streaming import MirrorThread, WriterThread, MediaDownloaderThread


class TestValidateStatus():

    @pytest.fixture(
            params=[
                [True, True],
                [True, False],
                [False, True],
                [False, False]
            ],
            ids=lambda p : ''.join(['T' if s else 'F' for s in p])
    )
    def filter_funcs(self, mocker, request):
        """A list of filter functions with parameterized return values"""
        return [
                mocker.Mock(spec=lambda s : 1, return_value=r)
                for r in request.param
        ]

    def test_all_funcs_called(self, worker_class, status, filter_funcs):
        worker_class.validate_status(status, filter_funcs)
        for func in filter_funcs:
            func.assert_called_once_with(status)

    def test_return_value(self, worker_class, status, filter_funcs):
        actual = worker_class.validate_status(status, filter_funcs)
        expected = all( [f(status) for f in filter_funcs ] )
        assert(actual == expected)

@pytest.mark.usefixtures('patch_remove_urls')
class TestProcessStatus():

    @pytest.mark.usefixtures('validate_true')
    def test_validate_status_called(self, subworker, status):
        subworker.process_status(status)
        subworker.validate_status.assert_called_once()

    @pytest.mark.usefixtures('validate_true')
    def test_validate_status_call_args(self, subworker, status):
        subworker.process_status(status)
        subworker.validate_status.assert_called_once_with(status, subworker.filters)

    @pytest.mark.usefixtures('validate_false', 'patch_statics')
    def test_abort_when_invalid(self, subworker, status, static_func):
        subworker.process_status(status)
        static_func.assert_not_called()

    @pytest.mark.usefixtures('validate_true', 'patch_statics')
    def test_static_call_made_when_valid(self, subworker, status, static_func):
        subworker.process_status(status)
        static_func.assert_called_once()

class TestWriterDefault():

    def test_return(self, status, inject_retweeted):
        actual = WriterThread.default_filter(status)
        expected = not inject_retweeted
        assert(actual == expected)

class TestMirrorDefault():

    def test_fail_on_mention(self, status, inject_mentions):
        valid = MirrorThread.default_filter(status)
        assert(status.user_mentions)
        assert(not valid)

    def test_fail_on_reply(self, status, inject_reply):
        valid = MirrorThread.default_filter(status)
        assert(status.in_reply_to_user_id)
        assert(not valid)

    def test_fail_on_retweeted(self, status, inject_retweeted):
        valid = MirrorThread.default_filter(status)
        assert(status.in_reply_to_user_id)
        assert(not valid)
