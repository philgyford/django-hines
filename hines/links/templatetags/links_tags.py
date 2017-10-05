from django import template
from ditto.pinboard.templatetags.ditto_pinboard import popular_bookmark_tags

register = template.Library()


@register.inclusion_tag('pinboard/includes/card_tags.html')
def popular_tags_card(limit=10):
    """
    """
    return {
            'card_title': 'Most-used tags',
            'tag_list': popular_bookmark_tags(limit=limit),
            }

