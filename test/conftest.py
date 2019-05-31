import pytest

from twitter import Api
from test.mocks import *
from test.patches import *
from test.injectors import *

# See link below for full sample of Status._json dict
# https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2

@pytest.fixture
def format_patcher(self, mocker, output_file):
    def patcher(retval):
        mock_fmt = mocker.MagicMock(spec_set=str, name='str.format()')
        mock_fmt.format.return_value = retval
        str.__format__ = mocker.PropertyMock(return_value=mock_fmt)
        return retval
    return patcher


@pytest.fixture
def api(mocker):
    return mocker.MagicMock(spec=twitter.Api, name='api')

@pytest.fixture
def media_urls(mock_media):
    return [ m.media_url_https for m in mock_media ]

@pytest.fixture
def media_files(media_urls):
    return [ os.path.basename(url) for url in media_urls ]

@pytest.fixture
def media_outputs(media_files, dirname):
    return [ os.path.join(dirname, url) for url in media_files ]

@pytest.fixture
def add_media(inject_media, mock_media):
    inject_media(mock_media)

@pytest.fixture
def remove_media(inject_media):
    inject_media(None)
