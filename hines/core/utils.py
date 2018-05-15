# coding: utf-8
from datetime import datetime
import pytz

from django.utils.html import strip_tags
from django.utils.text import Truncator

from markdownx.utils import markdownify as markdownifyx


def make_date(d):
    "For convenience."
    return datetime.strptime(d, "%Y-%m-%d").date()


def make_datetime(dt):
    "For convenience."
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


def datetime_now():
    "Just returns a datetime object for now in UTC, with UTC timezone."
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def markdownify(content):
    "Wrap the method, just in case we need to do something extray in future."
    md = markdownifyx(content)
    return md


def truncate_string(text, strip_html=True, chars=255, truncate=u'…', at_word_boundary=False):
    """Truncate a string to a certain length, removing line breaks and mutliple
    spaces, optionally removing HTML, and appending a 'truncate' string.

    Keyword arguments:
    strip_html -- boolean.
    chars -- Number of characters to return.
    at_word_boundary -- Only truncate at a word boundary, which will probably
        result in a string shorter than chars.
    truncate -- String to add to the end.
    """
    if strip_html:
        text = strip_tags(text)
    text = text.replace('\n', ' ').replace('\r', '')
    text = ' '.join(text.split())
    if at_word_boundary:
        if len(text) > chars:
            text = text[:chars].rsplit(' ', 1)[0] + truncate
    else:
        text = Truncator(text).chars(chars, html=False, truncate=truncate)
    return text


def expire_view_cache(path, key_prefix=None):
    """
    This function allows you to invalidate any item from the per-view cache.

    It probably won't work with things cached using the per-site cache
    middleware (because that takes account of the Vary: Cookie header).

    This assumes you're using the Sites framework.

    Arguments:

        * path: The URL of the view to invalidate, like `/blog/posts/1234/`.

        * key prefix: The same as that used for the cache_page()
          function/decorator (if any).
    """
    from django.conf import settings
    from django.contrib.sites.models import Site
    from django.core.cache import cache
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    print("EXPIRE", path)

    # Prepare meta data for our fake request.

    domain_parts = Site.objects.get_current().domain.split(':')
    request_meta = {'SERVER_NAME': domain_parts[0],}
    if len(domain_parts) > 1:
        request_meta['SERVER_PORT'] = domain_parts[1]

    print(request_meta)

    # Create a fake request object

    request = HttpRequest()
    request.method = 'GET'
    request.META = request_meta
    request.path = path

    if settings.USE_I18N:
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE

    # If this key is in the cache, delete it:

    try:
        cache_key = get_cache_key(request, key_prefix=key_prefix)
        print("KEY", cache_key)
        if cache_key:
            print("A")
            if cache.has_key(cache_key):
                print("B")
                cache.delete(cache_key)
                return (True, 'Successfully invalidated')
            else:
                print("C")
                return (False, 'Cache_key does not exist in cache')
        else:
            print("D")
            raise ValueError('Failed to create cache_key')
    except (ValueError, Exception) as e:
        print("E", e)
        return (False, e)
