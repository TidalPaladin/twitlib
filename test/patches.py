import pytest
from twitter import Api

# See link below for full sample of Status._json dict
# https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2

@pytest.fixture(autouse=True)
def patch_io(mocker, mock_open):
    mocker.patch('os.makedirs', autospec=True)
    mocker.patch('os.path.exists', return_value=True, autospec=True)
    mocker.patch('json.dump', autospec=True)
    mocker.patch('requests.get', autospec=True)

@pytest.fixture
def format_patcher(self, mocker, output_file):
    def patcher(retval):
        mock_fmt = mocker.MagicMock(spec_set=str, name='str.format()')
        mock_fmt.format.return_value = retval
        str.__format__ = mocker.PropertyMock(return_value=mock_fmt)
        return retval
    return patcher
