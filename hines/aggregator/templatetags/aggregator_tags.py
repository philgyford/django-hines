from django import template
from django.core.urlresolvers import reverse

def do_linked_date(parser, token):
    """
    For the linked_date template tag.
    Pass it a date object and a date format in strftime format and it will return
    a string formatted to that format, wrapped in an anchor tag linking to the 
    appropriate aggregator_day page.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, date_to_be_formatted, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return FormatDateNode(date_to_be_formatted, format_string)

class FormatDateNode(template.Node):
    def __init__(self, date_to_be_formatted, format_string):
        self.date_to_be_formatted = template.Variable(date_to_be_formatted)
        self.format_string = template.Variable(format_string)

    def render(self, context):
        try:
            actual_date = self.date_to_be_formatted.resolve(context)
            actual_format = self.format_string.resolve(context)
            return '<a href="%s">%s</a>' % (
                reverse(
                    'aggregator_day', 
                    kwargs={
                        'year':actual_date.year, 
                        'month':"%02d" % actual_date.month, 
                        'day':"%02d" % actual_date.day,
                    }
                ),
                actual_date.strftime(actual_format)
            )
        except template.VariableDoesNotExist:
            return ''

register = template.Library()
register.tag('linked_date', do_linked_date)


@register.simple_tag
def active(request, slug):
    """
    Returns 'active-exact' if we're exactly on /slug/,
    or 'active-within' if we're within that, eg /slug/2010/09/21/bibble/,
    or '' if neither of those apply.
    These can then be used for CSS classes in the main navigation.
    """
    import re
    css_class = ''
    
    if slug == '' and request.path == '/':
        # Home page.
        css_class = 'active-exact'
    elif '/'+slug+'/' == request.path:
        # Top-level slug page.
        css_class = 'active-exact'
    else:
        # Within this slug.
        pattern = "^/%s/" % slug

        if re.search(pattern, request.path):
            css_class = 'active-within'

    return css_class