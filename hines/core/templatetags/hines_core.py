# -*- coding: utf-8 -*-
import smartypants as _smartypants

from django import template
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from ditto.lastfm.templatetags.ditto_lastfm import top_artists


register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Utility filter for getting a value from a dict using its key.

    e.g. if:

        ages = {'bob': 37,}

    then:

        {{ ages|get_item:'bob' }}

    displays:

        37
    """
    return dictionary.get(key)


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
def display_time(dt, show='both', granularity=0, link_to_day=False):
    """Return the HTML to display a datetime nicely, wrapped in a <time> tag.

    dt -- The datetime.
    show -- 'time', 'date' or 'both'.
    granularity -- A number indicating how detailed the datetime is, based on
                    https://www.flickr.com/services/api/misc.dates.html
    link_to_day -- Add an <a href=""> link around the date to the day page.
                   (Ignored if show=='time'.)

    See also http://www.brucelawson.co.uk/2012/best-of-time/ for <time> tag.
    """
    # The date and time formats for display:
    d_fmt = '%-d&nbsp;%b&nbsp;%Y'
    t_fmt = '%H:%M'

    if granularity == 8:
        visible_str = 'circa %s' % dt.strftime('%Y')
        stamp = dt.strftime('%Y')

    elif granularity == 6:
        visible_str = 'sometime in %s' % dt.strftime('%Y')
        stamp = dt.strftime('%Y')

    elif granularity == 4:
        visible_str = 'sometime in %s' % dt.strftime('%b&nbsp;%Y')
        stamp = dt.strftime('%Y-%m')

    else:

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


@register.filter
def smartypants(text):
    """
    Processes the text with smartypants.
    """
    return _smartypants.smartypants(text)


@register.inclusion_tag('hines_core/includes/card_lastfm_artists.html')
def lastfm_top_artists_card(limit=10, date=None, period='day'):
    """
    Displays the most listened-to Artists for all accounts.
    """
    card_title = 'Most listened-to music artists'
    more = None

    if date is None:
        more = {'text': 'More at Last.fm',
                'url': 'https://www.last.fm/user/gyford',}
    else:
        if period == 'day':
            card_title += ' on this day'
        elif period == 'month':
            card_title += ' this month'
        elif period == 'year':
            card_title += ' this year'

    return {
            'card_title': card_title,
            'artist_list': top_artists(limit=limit, date=date, period=period),
            'more': more,
            }

