# coding: utf-8
from datetime import datetime
import pytz

from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.utils.text import Truncator

from markdown import markdown

from . import app_settings


def make_date(d):
    "For convenience."
    return datetime.strptime(d, "%Y-%m-%d").date()


def make_datetime(dt):
    "For convenience."
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


def datetime_now():
    "Just returns a datetime object for now in UTC, with UTC timezone."
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def markdownify(content, output_format="xhtml"):
    """Wrap the method, just in case we need to do something extra in future.
    output_format is one of "xhtml" or "html5".
    """
    return markdown(
        text=content, extensions=["fenced_code"], output_format=output_format
    )


def truncate_string(
    text, strip_html=True, chars=255, truncate=u"…", at_word_boundary=False
):
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
    text = text.replace("\n", " ").replace("\r", "")
    text = " ".join(text.split())
    if at_word_boundary:
        if len(text) > chars:
            text = text[:chars].rsplit(" ", 1)[0] + truncate
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

    # Prepare metadata for our fake request.
    # I'm not sure how 'real' this data needs to be, but still:

    domain_parts = Site.objects.get_current().domain.split(":")
    request_meta = {"SERVER_NAME": domain_parts[0]}
    if len(domain_parts) > 1:
        request_meta["SERVER_PORT"] = domain_parts[1]
    else:
        request_meta["SERVER_PORT"] = "80"

    # Create a fake request object

    request = HttpRequest()
    request.method = "GET"
    request.META = request_meta
    request.path = path

    if settings.USE_I18N:
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE

    # If this key is in the cache, delete it:

    try:
        cache_key = get_cache_key(request, key_prefix=key_prefix)
        if cache_key:
            if cache.get(cache_key):
                cache.delete(cache_key)
                return (True, "Successfully invalidated")
            else:
                return (False, "Cache_key does not exist in cache")
        else:
            raise ValueError("Failed to create cache_key")
    except (ValueError, Exception) as e:
        return (False, e)


def get_site_url():
    """
    Returns the full domain of the website.
    Shouldn't end in a slash, so it can be used with static() etc.
    """
    protocol = "http"

    try:
        if app_settings.USE_HTTPS:
            protocol = "https"
    except AttributeError:
        pass

    domain = Site.objects.get_current().domain

    return "{}://{}".format(protocol, domain)
