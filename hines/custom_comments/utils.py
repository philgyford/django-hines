# coding: utf-8
import re

import bleach
from bleach.linkifier import Linker

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
    # Remove disallowed tags and attributes, and close open tags:
    comment = bleach.clean(
        comment,
        tags=get_allowed_tags(),
        attributes=get_allowed_attributes(),
        strip=True,
    )

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

    # Make URLs into links, truncating long ones:
    linker = Linker(callbacks=[bleach.callbacks.nofollow, shorten_url])
    comment = linker.linkify(comment)

    # Replace more than two newlines with two:
    comment = re.sub(r"\n\s*\n", "\n\n", comment)

    # Strip leading/trailing spaces:
    comment = comment.strip()

    return comment
