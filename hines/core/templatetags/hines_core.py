from django import template
from django.core.urlresolvers import reverse
from django.utils.html import format_html


register = template.Library()


@register.simple_tag(takes_context=True)
def current_url_name(context):
    """
    Returns the name of the current URL, namespaced, or False.

    Example usage:

        {% current_url_name as url_name %}

        <a href="#"{% if url_name == 'myapp:home' %} class="active"{% endif %}">Home</a>

    """
    url_name = False
    if context.request.resolver_match:
        url_name = "{}:{}".format(
                                context.request.resolver_match.namespace,
                                context.request.resolver_match.url_name
                            )
    return url_name


@register.simple_tag
def display_time(dt, link_to_day=False):
    """Return the HTML to display a datetime nicely.

    dt -- The datetime.
    view -- Nothing or 'detail' or 'day', probably.

    For a 'day' view, just returns the date/time as text.
    For other views returns it including a link to the ditto:day_archive page
        for that date.
    Both wrapped in a <time> tag.

    See also http://www.brucelawson.co.uk/2012/best-of-time/ for <time> tag.
    """

    stamp = dt.strftime('%Y-%m-%d %H:%M:%S')

    # The date and time formats for display:
    d_fmt = '%-d&nbsp;%b&nbsp;%Y'
    t_fmt = '%H:%M'

    if link_to_day:
        url = reverse('hines:day_archive', kwargs={
                    'year':     dt.strftime('%Y'),
                    'month':    dt.strftime('%m'),
                    'day':      dt.strftime('%d'),
                })

        visible_time = '%(time)s on <a href="%(url)s" title="All items from this day">%(date)s</a>' % {
                'time': dt.strftime(t_fmt),
                'url': url,
                'date': dt.strftime(d_fmt),
            }
    else:
        visible_time = dt.strftime(t_fmt + ' on ' + d_fmt)

    return format_html('<time datetime="%(stamp)s">%(visible)s</time>' % {
                'stamp': stamp,
                'visible': visible_time
            })

