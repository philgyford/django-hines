from django import template

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

