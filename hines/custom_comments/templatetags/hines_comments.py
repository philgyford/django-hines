from django import template
from django.template.defaultfilters import pluralize

from ..utils import clean_comment, get_allowed_tags

register = template.Library()


@register.filter
def clean(value):
    return clean_comment(value)


@register.simple_tag
def allowed_tags():
    """
    Returns a list of tags that are allowed in comments.
    """
    return get_allowed_tags()


@register.simple_tag
def commenting_status_message(post, allowed, close_after_days):
    """
    Generate a message describing why comments aren't allowed on a Post.
    If comments ARE allowed, it returns an empty string.

    Keyword arguments:
    post - The Post object.
    allowed - The global app_settings.COMMENTS_ALLOWED value.
    close_after_days - The global app_settings.COMMENTS_CLOSE_AFTER_DAYS
                       value.
    """
    message = ""

    if not allowed:
        message = "Commenting is turned off."
    elif not post.blog.allow_comments:
        message = "Commenting is turned off on this blog."
    elif not post.allow_comments:
        message = "Commenting is turned off for this post."
    elif not post.comments_are_open:
        plural = pluralize(close_after_days)
        message = (
            "Commenting is disabled on posts once they’re "
            f"{close_after_days} day{plural} old."
        )
    elif not post.comments_allowed:
        # There shouldn't be any other reasons why they're not allowed,
        # but just in case:
        message = "Commenting is currently turned off."

    return message
