# coding: utf-8
from datetime import datetime
import pytz
import re
from urllib.parse import urlparse, parse_qsl, unquote_plus

from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.utils.text import Truncator

import markdown2

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

    We used to use the markdown module, but now use markdown2. For changing the style
    of links (between xml-style and html5-style) it uses a boolean, html4tags. But
    we're sticking with the output_format of "xhtml" or "html5" that was used directly
    with the markdown module, and converting it.

    Extras used:

    * fenced-code-blocks - Enabled code blocks to be indicated with ```
        before and after the code. If pygments is installed, it also
        adds HTML tags to enable colouring if a syntax is indicated:
            ```python
            print("hi")
            ```
        https://github.com/trentm/python-markdown2/wiki/fenced-code-blocks

    * link-patterns - To make bare links in text clickable.
        https://github.com/trentm/python-markdown2/wiki/link-patterns
    """
    # We want any bare links in the text to be converted to links,
    # and still want any <a href=""> tags, and []() Markdown links,
    # to be converted normally.
    pattern = (
        r"((([A-Za-z]{3,9}:(?:\/\/)?)"  # scheme
        r"(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+(:\[0-9]+)?"  # user@hostname:port
        r"|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)"  # www.|user@hostname
        r"((?:\/[\+~%\/\.\w\-_]*)?"  # path
        r"\??(?:[\-\+=&;%@\.\w_]*)"  # query parameters
        r"#?(?:[\.\!\/\\\w]*))?)"  # fragment
        r"(?![^<]*?(?:<\/\w+>|\/?>))"  # ignore anchor HTML tags
        r"(?![^\(]*?\))"  # ignore links in brackets (Markdown links and images)
    )
    link_patterns = [(re.compile(pattern), r"\1")]

    return markdown2.markdown(
        content,
        extras=["fenced-code-blocks", "link-patterns"],
        html4tags=(output_format == "html5"),
        link_patterns=link_patterns,
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
    Returns the full domain of the website preceded by "http(s)://"

    Shouldn't end in a slash, so it can be used with static() etc.
    (Although it appears to return URLs ending in slashes?)
    """
    protocol = "http"

    try:
        if app_settings.USE_HTTPS:
            protocol = "https"
    except AttributeError:
        pass

    domain = Site.objects.get_current().domain

    return "{}://{}".format(protocol, domain)


class Url(object):
    """
    A url object that can be compared with other url orbjects
    without regard to the vagaries of encoding, escaping, and ordering
    of parameters in query strings.

    e.g.

        if Url(url1) == Url(url2):
            print("equal URLs")

    https://stackoverflow.com/a/9468284/250962

    We only use this (at time of writing) via the urls_are_equal()
    function below.
    """

    def __init__(self, url):
        parts = urlparse(url)
        _query = frozenset(parse_qsl(parts.query))
        _path = unquote_plus(parts.path)
        parts = parts._replace(query=_query, path=_path)
        self.parts = parts

    def __eq__(self, other):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)


def urls_are_equal(url1, url2, ignore_scheme=None):
    """
    Test whether two URLs are equal

    If ignore_schema is "http" then we ignore any difference in
    http/https in the URLs. Otherwise this matters.

    Order of query string arguments does not matter.
    Different #fragments do matter.
    """
    url1 = Url(url1)
    url2 = Url(url2)

    if ignore_scheme == "http":
        if url1.parts.scheme in ["http", "https"] and url2.parts.scheme in [
            "http",
            "https",
        ]:
            url1.parts = url1.parts._replace(scheme="")
            url2.parts = url2.parts._replace(scheme="")

    return url1 == url2
