import pytest
import twitlib.filters as filters
from twitter import User, Media, Hashtag

class TestRTGame():

    @pytest.fixture
    def text_format(self):
        return 'Test text\n {inject} test #hashtag'

    @pytest.fixture(params=[
        'rtGame',
        'RTGame',
        'RT GAME',
        'retweet game',
        'rt game',
        'Retweet Game'
    ])
    def match_text(self, text_format, request):
        inject = request.param
        return text_format.format(inject=inject)

    @pytest.fixture
    def no_match_text(self, text_format):
        return text_format.format(inject='')

    def test_positive_match(self, mocker, status, match_text):
        type(status).text = mocker.PropertyMock(return_value=match_text)
        match = filters.is_rt_game(status)
        assert(match)

    def test_negative_match(self, mocker, status, no_match_text):
        type(status).text = mocker.PropertyMock(return_value=no_match_text)
        match = filters.is_rt_game(status)
        assert(not match)

class TestIsReply():

    @pytest.fixture(params=[100, None], ids=['user', 'nouser'])
    def reply_user(self, mocker, status, request):
        val = request.param
        type(status).in_reply_to_user_id = mocker.PropertyMock(return_value=val)
        return val

    @pytest.fixture(params=[100, None], ids=['status', 'nostatus'])
    def reply_status(self, mocker, status, request):
        val = request.param
        type(status).in_reply_to_status_id = mocker.PropertyMock(return_value=val)
        return val

    def test_is_reply(self, status, reply_user, reply_status):
        expected = bool(reply_user or reply_status)
        actual = filters.is_reply(status)
        assert(expected == actual)

class TestHasMentions():

    @pytest.fixture(params=[1, 2])
    def mentions(self, mocker, status, request):
        num_mentions = request.param
        mentions = [
                mocker.MagicMock(spec_set=User, name='mention%i' % i)
                for i in range(num_mentions)
        ]
        type(status).user_mentions = mocker.PropertyMock(return_value=mentions)
        return mentions

    @pytest.fixture
    def no_mentions(self, mocker, status):
        type(status).user_mentions = mocker.PropertyMock(return_value=None)

    def test_has_mentions(self, status, mentions):
        mentions = filters.has_mentions(status)
        assert(mentions)

    def test_no_mentions(self, status, no_mentions):
        mentions = filters.has_mentions(status)
        assert(not mentions)

class TestTweetedBy():

    @pytest.fixture
    def tweeted_by(self, mocker, status):
        id = 1000
        type(status).user = mocker.PropertyMock(spec_set=User)
        type(status.user).id = mocker.PropertyMock(return_value=id)
        return id

    @pytest.fixture
    def not_tweeted_by(self, tweeted_by):
        return tweeted_by + 2

    def test_tweeted_by(self, status, tweeted_by):
        result = filters.tweeted_by(status, tweeted_by)
        assert(result)

    def test_not_tweeted_by(self, status, not_tweeted_by):
        result = filters.tweeted_by(status, not_tweeted_by)
        assert(not result)

class TestIsRetweet():

    @pytest.fixture
    def retweet(self, mocker, status):
        type(status).retweeted_status = mocker.PropertyMock(return_value=True)
        return True

    @pytest.fixture
    def not_retweet(self, mocker, status):
        type(status).retweeted_status = mocker.PropertyMock(return_value=False)
        return False

    def test_retweet(self, status, retweet):
        result = filters.is_retweet(status)
        assert(result)

    def test_not_retweet(self, status, not_retweet):
        result = filters.is_retweet(status)
        assert(not result)

class TestHasMedia():

    @pytest.fixture(params=[1, 2])
    def media(self, mocker, status, request):
        num_media = request.param
        media = [
                mocker.MagicMock(spec_set=Media, name='media%i' % i)
                for i in range(num_media)
        ]
        type(status).media = mocker.PropertyMock(return_value=media)
        return media

        return True

    @pytest.fixture
    def no_media(self, mocker, status):
        type(status).media = mocker.PropertyMock(return_value=None)

    def test_has_media(self, status, media):
        result = filters.has_media(status)
        assert(result)

    def test_no_media(self, status, no_media):
        result = filters.has_media(status)
        assert(not result)

class TestHasHashtag():

    @pytest.fixture
    def target_hashtag(self, mocker, status):
        result =  mocker.MagicMock(
                spec=Hashtag(),
                name='target_hastag'
        )
        return result

    @pytest.fixture
    def noise_hashtag(self, mocker, status):
        result =  mocker.MagicMock(
                spec=Hashtag(),
                name='target_hastag'
        )
        return result


    def test_no_hashtag(self, status, inject_hashtag):
        inject_hashtag(None)
        has_hashtag = filters.has_hashtag(status, 'null')
        assert(not has_hashtag)

    def test_wrong_hashtag(self, status, noise_hashtag, target_hashtag, inject_hashtag):
        inject_hashtag([noise_hashtag])
        text = target_hashtag.text
        has_hashtag = filters.has_hashtag(status, text)
        assert(not has_hashtag)

    def test_right_hashtag(self, status, noise_hashtag, target_hashtag, inject_hashtag):
        inject_hashtag([target_hashtag, noise_hashtag])
        text = target_hashtag.text
        has_hashtag = filters.has_hashtag(status, text)
        assert(has_hashtag)

    def test_ignore_case_true(self, status, target_hashtag, inject_hashtag):
        text = 'FOO'
        target_hashtag.text = 'foo'
        inject_hashtag([target_hashtag])
        has_hashtag = filters.has_hashtag(status, text, ignore_case=True)
        assert(has_hashtag)

    def test_ignore_case_false(self, status, target_hashtag, inject_hashtag):
        text = 'FOO'
        target_hashtag.text = 'foo'
        inject_hashtag([target_hashtag])
        has_hashtag = filters.has_hashtag(status, text, ignore_case=False)
        assert(not has_hashtag)
