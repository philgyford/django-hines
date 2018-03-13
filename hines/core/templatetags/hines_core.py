# -*- coding: utf-8 -*-
import re
from urllib.parse import urlparse

import smartypants as _smartypants

from django import template
from django.urls import reverse
from django.template.defaultfilters import linebreaks_filter
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from ditto.lastfm.templatetags.ditto_lastfm import (
    recent_scrobbles, top_artists
)

from spectator.events.templatetags.spectator_events import (
    most_seen_creators_by_works_card
)


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

    # In 400 and 500 error templates context has no 'request':
    if hasattr(context, 'request'):
        if context.request.resolver_match:
            url_name = "{}:{}".format(
                                context.request.resolver_match.namespace,
                                context.request.resolver_match.url_name
                            )
    return url_name


@register.simple_tag
def display_time(dt=None, show='both', granularity=0, link_to_day=False):
    """Return the HTML to display a datetime nicely, wrapped in a <time> tag.

    dt -- The datetime. If None, then the current time is used.
    show -- 'time', 'date' or 'both'.
    granularity -- A number indicating how detailed the datetime is, based on
                    https://www.flickr.com/services/api/misc.dates.html
    link_to_day -- Add an <a href=""> link around the date to the day page.
                   (Ignored if show=='time'.)

    See also http://www.brucelawson.co.uk/2012/best-of-time/ for <time> tag.
    """

    if dt is None:
        dt = now()

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
    return mark_safe(_smartypants.smartypants(text))


@register.inclusion_tag('hines_core/includes/card_lastfm_scrobbles.html')
def lastfm_recent_scrobbles_card(limit=10):
    """
    Displays the most recent Scrobbles for all accounts.
    """
    more = {'text': 'More at Last.fm',
            'url': 'https://www.last.fm/user/gyford',}

    return {
            'card_title': 'Recently played',
            'scrobble_list': recent_scrobbles(limit=limit),
            'more': more,
            }


@register.inclusion_tag('hines_core/includes/card_lastfm_artists.html')
def lastfm_top_artists_card(limit=10, date=None, period='day'):
    """
    Displays the most listened-to Artists for all accounts.
    """
    card_title = 'Most listened-to artists'
    more = None

    if date is None:
        more = {'text': 'More at Last.fm',
                'url': 'https://www.last.fm/user/gyford',}
    else:
        if period == 'day':
            pass
            # card_title += ' on this day'
        elif period == 'month':
            card_title += ' this month'
        elif period == 'year':
            card_title += ' this year'

    return {
            'card_title': card_title,
            'artist_list': top_artists(limit=limit, date=date, period=period),
            'more': more,
            }


@register.filter
def linebreaks_first(text):
    """
    Does the same as the standard Djanago `linebreaks` filter:

    Replace line breaks in plain text with appropriate HTML; a single
    newline becomes an HTML line break (``<br />``) and a new line
    followed by a blank line becomes a paragraph break (``</p>``).

    But also adds the CSS class 'first' to the first paragraph tag.

    Used for old Weblog post_detail templates.
    """
    text = linebreaks_filter(text)
    text = re.sub(r'^<p>', '<p class="first">', text)
    return mark_safe(text)


@register.filter
def domain_urlize(value):
    """
    Returns an HTML link to the supplied URL, but only using the domain as the
    text.

    e.g. if `my_url` is 'http://www.example.org/foo/' then:

        {{ my_url|domain_urlize }}

    returns:
        <a href="http://www.example.org/foo/" rel="nofollow">www.example.org</a>
    """
    parsed_uri = urlparse(value)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return format_html('<a href="{}" rel="nofollow">{}</a>',
            value,
            domain
        )


@register.inclusion_tag('spectator_core/includes/card_chart.html')
def most_seen_directors_card(num=10):
    """
    Custom wrapper around
    """
    num = num + 1
    data = most_seen_creators_by_works_card(
                            num=num, work_kind='movie', role_name='Director')

    prev_creator = None
    coens = ['Joel Coen', 'Ethan Coen']
    coen_position = None

    creators = data['object_list']

    for n, creator in enumerate(creators):
        if prev_creator:
            if prev_creator.name in coens and creator.name in coens:
                coen_position = (n - 1)
                break
        prev_creator = creator

    if coen_position is not None:
        coen1 = creators[coen_position]
        coen2 = creators[coen_position + 1]
        creators[coen_position] = [ coen1, coen2 ]
        del( creators[coen_position + 1] )

    for m in range(coen_position + 1, len(creators)):
        creators[m].chart_position = creators[m].chart_position - 1


    data['card_title'] = 'Most seen film directors'

    data['object_list'] = creators

    return data
