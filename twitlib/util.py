import json
import re

def list_media(status):
    """
    Lists media URLs in a twitter.Status object

    Args
    ===
        status : twitter.Status
    Status object to extract media from

    Return
    ===
    list(str) : List of URLs or [] if the status has no media
    """
    media = status.media
    return [m.media_url_https for m in media] if media else []

def remove_urls(text):
    """
    Removes twitter short URLS from a string and returns the result.
    URLs are matched by the substring 'https://t.co'. If the string
    contains no matching URLs, the returned string is identical to
    the input string.
    """
    text = re.sub(r"https://t.co\S+", "", text)
    return re.sub(r"\s+", " ", text)
