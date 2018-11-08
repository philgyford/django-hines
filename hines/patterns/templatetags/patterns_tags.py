from django import template
from django.template.loader import get_template
from django.utils.html import escape


register = template.Library()


@register.simple_tag()
def verbatim_include(name):
    """
    Include a template escaped, so its raw HTML appears on the page.

    Example: {% verbatim_include "weblog/post.html" %}
    """
    template = get_template(name)
    return escape(template.render())
