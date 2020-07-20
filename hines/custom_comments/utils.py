# coding: utf-8
import re

import bleach
from bleach.linkifier import Linker
from django_comments import signals
from django_comments.models import CommentFlag

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_str

from hines.core import app_settings
from .pykismet3 import Akismet


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


def is_akismet_spam(sender, comment, request):
    """
    Test whether a comment is spam or not, according to Akismet.

    Returns True if probably spam, False otherwise.

    comment - The Comment object
    request - The Request object
    """

    if comment.user and comment.user.is_staff:
        # Don't test comments posted by staff/admin
        return False

    if not app_settings.AKISMET_API_KEY:
        # If it's not set we can't test.
        return False

    protocol = "http" if not request.is_secure() else "https"
    host = protocol + "://" + request.get_host()
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])

    # URL of the Post the Comment was posted on
    parent_object_url = comment.content_object.get_absolute_url()

    data = {
        "user_ip": ip_address,
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "referrer": request.POST.get("referrer", ""),
        # "The full permanent URL of the entry the comment was submitted to.":
        "permalink": f"{host}{parent_object_url}",
        "comment_type": "comment",
        "comment_content": smart_str(comment.comment),
        "blog_lang": "en",
        "blog_charset": "UTF-8",
    }

    if comment.user:
        # Posted by a logged-in user.
        data["comment_author"] = comment.user.get_full_name()
        data["comment_author_email"] = comment.user.email
        if comment.user.url:
            data["comment_author_url"] = comment.user.url
    else:
        data["comment_author"] = comment.user_name
        data["comment_author_email"] = comment.user_email
        if comment.user_url:
            data["comment_author_url"] = comment.user_url

    if settings.DEBUG:
        data["is_test"] = 1

    # You can ensure a spam response by adding this:
    # data["comment_author"] = "viagra-test-123"

    a = Akismet(blog_url=host, user_agent="")
    a.api_key = app_settings.AKISMET_API_KEY

    return a.check(data)


def test_comment_for_spam(sender, comment, request, **kwargs):
    """
    Tests a comment to see if it's probably spam.
    If so, marks it as not public.
    Called from a signal.
    """

    if is_akismet_spam(sender, comment, request):
        # A flag has to be flagged by a person.
        # So we're just going to get the first superuser.
        user_model = get_user_model()
        user = user_model.objects.filter(is_superuser=True, is_active=True)[0]

        # If we just do create() here then we get an error if this flagged spam
        # comment has identical content to a previously-flagged spam comment.
        # So this ensure we don't try and create duplicate flags:
        flag, created = CommentFlag.objects.get_or_create(
            user=user, comment=comment, flag="Spam",
        )
        signals.comment_was_flagged.send(
            sender=comment.__class__,
            comment=comment,
            flag=flag,
            created=created,
            request=request,
        )
        comment.is_public = False
        comment.save()

        # Add a message which will be displayed in comment_form.html
        # (as well as wherever messages are usually displayed).
        # It will have tags like "spam warning".
        message_content = "Your post was flagged as possible spam."

        managers = getattr(settings, "MANAGERS", [])

        # Just in case MANAGERS isn't set or is empty:
        if len(managers) > 0:
            message_content += (
                " If it wasn't then "
                '<a href="mailto:%s?subject=Flagged comment (ID: %s)">email me</a> '
                "to have it published." % (managers[0][1], comment.id)
            )

        add_comment_message(request, messages.WARNING, message_content)


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