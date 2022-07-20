from ditto.pinboard.templatetags.ditto_pinboard import popular_bookmark_tags
from django import template

register = template.Library()


@register.inclusion_tag("links/includes/card_tags.html")
def popular_tags_card(limit=10):
    return {
        "card_title": "Most-used tags",
        "tag_list": popular_bookmark_tags(limit=limit),
    }
