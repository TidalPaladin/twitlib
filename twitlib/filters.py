from twitter import Status

def is_reply(status):
    if status.in_reply_to_user_id:
        return True
    if status.in_reply_to_status_id:
        return True
    return False

def has_mentions(status):
    return status.user_mentions is not None

def tweeted_by(status, id):
    return status.user.id == id

def is_retweet(status):
    return status.retweeted_status

def has_media(status):
    return bool(status.media)

def has_hashtag(status, tag_name, ignore_case=False):
    if not status.hashtags:
        return False

    if ignore_case:
        tag_name = tag_name.lower()
        tag_texts = [tag.text.lower() for tag in status.hashtags]
    else:
        tag_texts = [tag.text for tag in status.hashtags]
    return tag_name in tag_texts
