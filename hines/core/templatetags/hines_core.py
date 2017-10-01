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
def display_time(dt, show='both', link_to_day=False):
    """Return the HTML to display a datetime nicely, wrapped in a <time> tag.

    dt -- The datetime.
    show -- 'time', 'date' or 'both'.
    link_to_day -- Add an <a href=""> link around the date to the day page.
                   (Ignored if show=='time'.)

    See also http://www.brucelawson.co.uk/2012/best-of-time/ for <time> tag.
    """
    # The date and time formats for display:
    d_fmt = '%-d&nbsp;%b&nbsp;%Y'
    t_fmt = '%H:%M'

    if show == 'time':
        visible_str = dt.strftime(t_fmt)
    else:
        # Date only or time and date:

        if link_to_day:
            url = reverse('hines:day_archive', kwargs={
                        'year':     dt.strftime('%Y'),
                        'month':    dt.strftime('%m'),
                        'day':      dt.strftime('%d'),
                    })

            visible_str = '<a href="%(url)s" title="All items from this day">%(date)s</a>' % {
                    'url': url,
                    'date': dt.strftime(d_fmt),
                }
        else:
            visible_str = dt.strftime(d_fmt)

        if show == 'both':
            # Add the time:
            visible_str = '%s on %s' % (dt.strftime(t_fmt), visible_str)

    stamp = dt.strftime('%Y-%m-%d %H:%M:%S')

    return format_html('<time datetime="%(stamp)s">%(visible)s</time>' % {
                'stamp': stamp,
                'visible': visible_str
            })

