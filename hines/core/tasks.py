from io import StringIO

from django.core.management import call_command

# One django-q task for every management command that we want to call.
#
# The Kwargs argument for a Task should be of the format:
#   days="1", account="gyford"


def fetch_flickr_photos(days="30", account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_flickr_photos", stdout=out, days=days, account=account)
    return out.getvalue()


def fetch_flickr_photosets(account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_flickr_photosets", stdout=out, account=account)
    return out.getvalue()


def fetch_lastfm_scrobbles(days="1", account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_lastfm_scrobbles", stdout=out, days=days, account=account)
    return out.getvalue()


def fetch_pinboard_bookmarks(recent="20", account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_pinboard_bookmarks", stdout=out, recent=recent, account=account)
    return out.getvalue()


def fetch_twitter_favorites(recent="200", account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_twitter_favorites", stdout=out, recent=recent, account=account)
    return out.getvalue()


def fetch_twitter_files():
    out = StringIO()
    call_command("fetch_twitter_files", stdout=out)
    return out.getvalue()


def fetch_twitter_tweets(recent="200", account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("fetch_twitter_tweets", stdout=out, recent=recent, account=account)
    return out.getvalue()


def pending_mentions():
    out = StringIO()
    call_command("pending_mentions", stdout=out)
    return out.getvalue()


def publish_scheduled_posts():
    out = StringIO()
    call_command("publish_scheduled_posts", stdout=out)
    return out.getvalue()


def update_twitter_tweets(account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("update_twitter_tweets", stdout=out, account=account)
    return out.getvalue()


def update_twitter_users(account=None):
    if account is None:
        return False

    out = StringIO()
    call_command("update_twitter_users", stdout=out, account=account)
    return out.getvalue()
