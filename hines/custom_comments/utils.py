import re

import bleach
from bleach.linkifier import Linker

from django.conf import settings


def get_allowed_tags():
    "Use our custom list of allowed tags, if any, else Bleach's default."
    if hasattr(settings, 'HINES_COMMENTS_ALLOWED_TAGS') and settings.HINES_COMMENTS_ALLOWED_TAGS:
        return settings.HINES_COMMENTS_ALLOWED_TAGS
    else:
        return bleach.sanitizer.ALLOWED_TAGS


def get_allowed_attributes():
    "Use our custom dict of allowed attributes, if any, else Bleach's default."
    if hasattr(settings, 'HINES_COMMENTS_ALLOWED_ATTRIBUTES') and settings.HINES_COMMENTS_ALLOWED_ATTRIBUTES:
        return settings.HINES_COMMENTS_ALLOWED_ATTRIBUTES
    else:
        return bleach.sanitizer.ALLOWED_ATTRIBUTES


def clean_comment(comment, max_url_length=30):
    """
    Strip disallowed tags, add rel=nofollow to links, remove extra newlines.

    comment - The string to be cleaned.
    max_url_length - URLs longer than this will have their visible version
                     truncated.
    """
    # Remove disallowed tags and attributes, and close open tags:
    comment = bleach.clean(comment,
                            tags=get_allowed_tags(),
                            attributes=get_allowed_attributes(),
                            strip=True)

    def shorten_url(attrs, new=False):
        """Shorten overly-long URLs in the text."""
        # Only adjust newly-created links
        if not new:
            return attrs
        # _text will be the same as the URL for new links
        text = attrs[u'_text']
        if len(text) > max_url_length:
            attrs[u'_text'] = text[0:max_url_length-1] + '…'
        return attrs

    # Make URLs into links, truncating long ones:
    linker = Linker(callbacks=[bleach.callbacks.nofollow, shorten_url])
    comment = linker.linkify(comment)

    # Replace more than two newlines with two:
    comment = re.sub(r'\n\s*\n', '\n\n', comment)

    # Strip leading/trailing spaces:
    comment = comment.strip()

    return comment

