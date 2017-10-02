# coding: utf-8
from datetime import datetime
import pytz

from django.utils.html import strip_tags
from django.utils.text import Truncator


def make_date(d):
    "For convenience."
    return datetime.strptime(d, "%Y-%m-%d").date()


def make_datetime(dt):
    "For convenience."
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


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

