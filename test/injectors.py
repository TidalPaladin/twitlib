"""
Fixtures that return injector functions
"""

import pytest

# See link below for full sample of Status._json dict
# https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2

#######################################################################
#               STATUS BASE
#######################################################################

@pytest.fixture
def inject_media(mocker, status):
    def injector(media):
        type(status).media = mocker.PropertyMock(return_value=media)
        return status.media
    return injector

@pytest.fixture
def inject_mentions(mocker, status):
    def injector(mentions):
        type(status).user_mentions = mocker.PropertyMock(return_value=mentions)
        return status.user_mentions
    return injector

@pytest.fixture
def inject_text(status, mocker):
    def injector(text):
        type(status).text = mocker.PropertyMock(return_value=text)
        return status.text
    return injector

@pytest.fixture
def inject_full_text(status, mocker):
    def injector(text):
        type(status).full_text = mocker.PropertyMock(return_value=text)
        return status.full_text
    return injector

@pytest.fixture
def inject_retweeted(mocker, status):
    def injector(value):
        val = mocker.PropertyMock(return_value=value)
        type(status).retweeted_status = val
        return status.retweeted_status
    return injector

@pytest.fixture
def inject_reply(mocker, status):
    def injector(value):

        if value:
            status_id = mocker.PropertyMock(spec_set=int, name='reply_status_id')
            user_id = mocker.PropertyMock(spec_set=int, name='reply_user_id')
            screen_name = mocker.PropertyMock(spec_set=str, name='reply_user_screen_name')
        else:
            status_id = mocker.PropertyMock(return_value=None)
            user_id = mocker.PropertyMock(return_value=None)
            screen_name = mocker.PropertyMock(return_value=None)

        type(status).in_reply_to_status_id = status_id
        type(status).in_reply_to_user_id = user_id
        type(status).in_reply_to_screen_name = screen_name

        return status_id, user_id, screen_name

    return injector

@pytest.fixture
def inject_extended(mocker, status, inject_full_text):
    def injector(value):
        type(status).truncated = mocker.PropertyMock(return_value=value)
        return status.truncated
    return injector

@pytest.fixture
def inject_hashtag(mocker, status):
    def injector(value):
        type(status).hashtags = mocker.PropertyMock(return_value=value)
        return status.hashtags
    return injector
