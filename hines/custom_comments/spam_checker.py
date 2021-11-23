from django.conf import settings
from django.contrib import messages

from django.utils.encoding import smart_str

import requests


AKISMET_CHECK_URL = "rest.akismet.com/1.1/comment-check"


def is_akismet_spam(comment, request):
    """
    Test whether a comment is spam or not, according to Akismet.

    Returns True if probably spam, False otherwise.

    comment - The Comment object
    request - The Request object
    """

    if comment.user and comment.user.is_staff:
        # Don't test comments posted by staff/admin.
        return False

    if not hasattr(settings, "HINES_AKISMET_API_KEY"):
        # If it's not set we can't test.
        return False

    protocol = "http" if not request.is_secure() else "https"
    host = protocol + "://" + request.get_host()
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META["REMOTE_ADDR"])

    # URL of the Post the Comment was posted on
    parent_object_url = comment.content_object.get_absolute_url()

    parameters = {
        "user_ip": ip,
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "referrer": request.POST.get("referrer", ""),
        # "The full permanent URL of the entry the comment was submitted to.":
        "permalink": f"{host}{parent_object_url}",
        "comment_type": "comment",
        "comment_content": smart_str(comment.comment),
        "blog": host,
        "blog_lang": "en",
        "blog_charset": "UTF-8",
    }

    if comment.user:
        # Posted by a logged-in user.
        parameters["comment_author"] = comment.user.display_name
        parameters["comment_author_email"] = comment.user.email
    else:
        parameters["comment_author"] = comment.user_name
        parameters["comment_author_email"] = comment.user_email

    if comment.user_url:
        parameters["comment_author_url"] = comment.user_url

    # When testing you can ensure a spam response by adding this:
    # parameters["comment_author"] = "viagra-test-123"

    headers = {"User-Agent": "Gyford.com/1.0"}

    r = requests.post(
        "https://" + settings.HINES_AKISMET_API_KEY + "." + AKISMET_CHECK_URL,
        data=parameters,
        headers=headers,
    )

    if r.text == "false":
        return False
    elif r.text == "true":
        return True
    else:
        # If there was an error from Akismet, say the comment isn't spam.
        messages.add_message(
            request,
            messages.ERROR,
            f"There was an error when testing the comment: {r.text}",
            extra_tags="danger",
        )
        return False


def test_comment_for_spam(sender, comment, request, **kwargs):
    """
    Tests a comment to see if it's probably spam.
    If so, marks it as not public.
    Called from a signal.

    NOTE: CommentFlags can't currently be used with custom Comment models,
    so won't work with CustomComments. So a load of the stuff below is
    commented out until we can get it working.
    """

    if is_akismet_spam(comment, request):
        # A flag has to be flagged by a person.
        # So we're just going to get the first superuser.
        # user_model = get_user_model()
        # user = user_model.objects.filter(is_superuser=True, is_active=True)[0]

        # If we just do create() here then we get an error if this flagged spam
        # comment has identical content to a previously-flagged spam comment.
        # So this ensure we don't try and create duplicate flags:

        # flag, created = CommentFlag.objects.get_or_create(
        #     user=user, comment=comment, flag="spam",
        # )
        # signals.comment_was_flagged.send(
        #     sender=comment.__class__,
        #     comment=comment,
        #     flag=flag,
        #     created=created,
        #     request=request,
        # )
        comment.is_public = False
        comment.save()

        # Add a message which should be displayed in a template.
        message_content = "Your post was flagged as possible spam."

        managers = getattr(settings, "MANAGERS", [])

        # Just in case MANAGERS isn't set or is empty:
        if len(managers) > 0:
            message_content += (
                " If it wasn't then "
                '<a href="mailto:%s?subject=Flagged comment (ID: %s)">email me</a> '
                "to have it published." % (managers[0][1], comment.id)
            )

        messages.add_message(
            request,
            messages.WARNING,
            message_content,
            extra_tags="message-kind-comment",
        )
