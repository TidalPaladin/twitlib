import pytest
from twitlib.util import *


class TestListMedia():

    @pytest.mark.usefixtures('remove_media')
    def test_without_media(self, status):
        actual = list_media(status)
        expected = []
        assert(actual == expected)

    @pytest.mark.usefixtures('add_media')
    def test_with_media(self, status, media_urls):
        assert(status.media)
        actual = list_media(status)
        expected = media_urls
        assert(actual == expected)

class TestRemoveUrls():

    @pytest.fixture
    def format_proto(self):
        return 'tweet text %s #hashtag'

    @pytest.fixture
    def expected(self, format_proto):
        return 'tweet text #hashtag'

    @pytest.fixture(params=[1, 2], ids=['1url', '2url'])
    def input(self, request, format_proto):

        num_urls = request.param
        urls = ' '.join([
            'https://t.co/Ax%iSeF.jpg' % i
            for i in range(num_urls)
        ])
        return format_proto % urls

    def test_urls(self, expected, input):
        actual = remove_urls(input)
        assert(actual == expected)

    def test_no_urls(self, expected, input):
        text = 'tweet text #hashtag'
        expected = text
        actual = remove_urls(text)
        assert(expected == actual)
