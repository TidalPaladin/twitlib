import pytest
import logging
import json
import requests
import twitter
import os

from twitlib.streaming import WorkerThread
from twitlib.streaming import MirrorThread, WriterThread, MediaDownloaderThread
import twitlib

class TestWrite():

    @pytest.fixture
    def output_file(self):
        return 'out_file.json'

    def test_return_filename(self, status, output_file):
        """Tests process_status() returns name of written file"""
        ret = WriterThread.write_status(status=status, filename=output_file)
        assert(ret == output_file)

    def test_opened_correct_file(self, status, output_file, mock_open):
        """Tests process_status() opens correct output_file for writing"""
        ret = WriterThread.write_status(status=status, filename=output_file)
        mock_open.assert_called_once_with(output_file, 'w', encoding='utf-32')

    def test_wrote_correct_content(self, status, output_file):
        """Tests process_status() opens correct output_file for writing"""
        ret = WriterThread.write_status(status=status, filename=output_file)
        json.dump.assert_called_once_with(status.AsDict(), twitlib.streaming.open(), indent=2, sort_keys=True)

@pytest.mark.usefixtures('add_media')
class TestDownload():

    @pytest.fixture
    def expected_files(self, mocker, media_outputs):
        expected = [
                mocker.call(f, 'wb')
                for f in media_outputs
        ]
        return expected

    def test_opened_correct_files(self, status, mock_open, dirname, expected_files):
        """Tests process_status() opens correct files for writing"""
        MediaDownloaderThread.download_media(status, dirname)
        actual = mock_open.call_args_list
        assert(status.media)
        assert(expected_files == actual)

    def test_wrote_correct_content(self, mocker, status, dirname, mock_open, media_urls):
        """Tests process_status() writes correct content"""
        content = [ requests.get(url) for url in media_urls ]
        expected = [ mocker.call(c.content) for c in content ]

        MediaDownloaderThread.download_media(status, dirname)
        actual = mock_open().write.call_args_list
        assert(expected == actual)

    def test_returns_file_list(self, mocker, status, dirname, mock_open, media_urls, media_outputs):
        """Tests process_status() returns list of written files"""
        expected = media_outputs
        actual = MediaDownloaderThread.download_media(status, dirname)
        assert(expected == actual)

    def test_mkdir_on_missing(self, mocker, status, dirname, mock_open):
        os.path.exists.return_value = False
        MediaDownloaderThread.download_media(status, dirname)
        os.path.exists.assert_called_once()
        os.makedirs.assert_called_once_with(dirname)

@pytest.mark.usefixtures('patch_remove_urls', 'remove_media')
class TestMirrorNoMedia():

    def test_calls_PostUpdate(self, status, api, dirname):
        MirrorThread.mirror(api, status, dirname)
        api.PostUpdate.assert_called_once()

    @pytest.mark.usefixtures('mock_downloader')
    def test_mirrored_text(self, status, api, dirname):
        MirrorThread.mirror(api, status, dirname)
        args, kwargs = api.PostUpdate.call_args
        expected = status.text
        actual = kwargs.get('status', None)
        assert(actual == expected)

    def test_raises_rate_limit_err(self, mocker, status, api, dirname):
        mocker.patch.object(api, 'PostUpdate', side_effect=twitter.TwitterError(''))
        with pytest.raises(twitter.TwitterError):
            MirrorThread.mirror(api, status, dirname)

    @pytest.mark.skip
    def test_catch_tweep_err(self, mocker, status, api, dirname):
        mocker.patch.object(api, 'PostUpdate', side_effect=twitter.TwitterError(''))
        MirrorThread.mirror(api, status, dirname)


@pytest.mark.usefixtures("patch_io", 'patch_remove_urls', 'add_media')
class TestMirror(TestMirrorNoMedia):
    """Non-truncated mirroring"""

    def test_posts_media_files(self, mocker, status, api, dirname, media_outputs, mock_open):
        MirrorThread.mirror(api, status, dirname)
        args, kwargs = api.PostUpdate.call_args

        actual = kwargs.get('media', None)
        expected = media_outputs
        assert(expected == actual)

    def test_calls_remove_urls(self, mocker, status, api, dirname, media_outputs, mock_open):
        MirrorThread.mirror(api, status, dirname)
        twitlib.util.remove_urls.assert_called_once_with(status.text)

    def test_uses_removed_url_text(self, mocker, status, api, dirname, media_outputs, mock_open):
        MirrorThread.mirror(api, status, dirname)
        args, kwargs = api.PostUpdate.call_args

        actual = kwargs.get('status', None)
        expected = twitlib.util.remove_urls.return_value
        assert(expected == actual)

    @pytest.mark.usefixtures('add_media')
    def test_media_dl_to_temp_dir(self, status, api, dirname, media_outputs, mock_downloader):
        MirrorThread.mirror(api, status, dirname)
        mock_downloader.download_media.assert_called_once_with(status, dirname)


@pytest.mark.usefixtures('patch_io', 'truncate', 'remove_media')
class TestMirrorTruncatedNoMedia(TestMirrorNoMedia):

    @pytest.fixture
    def full_text(self, mocker):
        return mocker.PropertyMock(spec_set=str, name='full_text')

    @pytest.fixture
    def truncate(self, full_text, inject_full_text, inject_extended):
        inject_full_text(full_text)
        inject_extended(True)

    @pytest.mark.usefixtures('mock_downloader')
    def test_mirrored_text(self, status, api, dirname, full_text):
        MirrorThread.mirror(api, status, dirname)
        twitlib.util.remove_urls.assert_called_once_with(status.full_text)
        args, kwargs = api.PostUpdate.call_args
        expected = twitlib.util.remove_urls.return_value
        actual = kwargs.get('status', None)
        assert(actual == expected)

@pytest.mark.usefixtures('truncate', 'add_media')
class TestMirrorTruncated(TestMirror):

    @pytest.fixture
    def full_text(self, mocker):
        return mocker.PropertyMock(spec_set=str, name='full_text')

    @pytest.fixture
    def truncate(self, full_text, inject_full_text, inject_extended):
        inject_full_text(full_text)
        inject_extended(True)

    @pytest.mark.usefixtures('mock_downloader')
    def test_mirrored_text(self, status, api, dirname, full_text):
        MirrorThread.mirror(api, status, dirname)
        twitlib.util.remove_urls.assert_called_once_with(status.full_text)
        args, kwargs = api.PostUpdate.call_args
        expected = twitlib.util.remove_urls.return_value
        actual = kwargs.get('status', None)
        assert(actual == expected)

    def test_calls_remove_urls(self, mocker, status, api, dirname, media_outputs, mock_open):
        MirrorThread.mirror(api, status, dirname)
        twitlib.util.remove_urls.assert_called_once_with(status.full_text)
