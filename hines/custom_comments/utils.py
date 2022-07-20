import re
from functools import partial

import bleach
from bleach import Cleaner
from bleach.linkifier import LinkifyFilter
from django.contrib import messages

from hines.core import app_settings


def get_allowed_tags():
    return app_settings.COMMENTS_ALLOWED_TAGS


def get_allowed_attributes():
    return app_settings.COMMENTS_ALLOWED_ATTRIBUTES


def clean_comment(comment, max_url_length=23):
    """
    Strip disallowed tags, add rel=nofollow to links, remove extra newlines.

    23 for the max_url_length is about the maximum when viewed on 320px device.

    comment - The string to be cleaned.
    max_url_length - URLs longer than this will have their visible version
                     truncated.
    """

    def shorten_url(attrs, new=False):
        """Shorten overly-long URLs in the text."""
        # Only adjust newly-created links
        if not new:
            return attrs
        # _text will be the same as the URL for new links
        text = attrs["_text"]

        # Trim the protocol off the start:
        for protocol in ["http://", "https://"]:
            if text.startswith(protocol):
                text = text[len(protocol) :]
                break

        if len(text) > max_url_length:
            attrs["_text"] = text[0 : max_url_length - 1] + "…"
        else:
            attrs["_text"] = text
        return attrs

    # Use a different regular expression to match URLs when creating
    # links because by default Bleach doesn't recognise any of the
    # newer TLDs like .rocks, .blog, etc.
    # via https://github.com/mozilla/bleach/issues/563#issuecomment-715586797
    URL_RE = re.compile(
        r"(?i)\b((?:(?:https?)://|www\d{0,3}[.])(?:[^\s()<>]+|"
        r"\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()"
        r"<>]+\)))*\)|[^\s`!()\[\]{};:" + r"'" + r'".,<>?«»“”‘’]))'
    )

    # Remove disallowed tags and attributes, and close open tags:
    cleaner = Cleaner(
        tags=get_allowed_tags(),
        attributes=get_allowed_attributes(),
        strip=True,
        filters=[
            # Make URLs into links, truncating long ones:
            partial(
                LinkifyFilter,
                callbacks=[bleach.callbacks.nofollow, shorten_url],
                url_re=URL_RE,
            )
        ],
    )

    comment = cleaner.clean(comment)

    # Replace more than two newlines with two:
    comment = re.sub(r"\n\s*\n", "\n\n", comment)

    # Strip leading/trailing spaces:
    comment = comment.strip()

    return comment


def add_comment_message(request, level, content):
    """
    So we have a single place for adding flash messages that will
    appear when submitting a comment.

    https://docs.djangoproject.com/en/3.0/ref/contrib/messages/

    Keyword arguments:
    request - The Request object
    level - One of the message levels, e.g. messages.SUCCESS
    content - The content of the message, a string.
    """
    messages.add_message(request, level, content, extra_tags="message-kind-comment")
