import re
from hashlib import md5
from urllib.parse import urlparse

import smartypants as _smartypants
from ditto.lastfm.templatetags.ditto_lastfm import recent_scrobbles, top_artists
from django import template
from django.template.defaultfilters import linebreaks_filter
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from spectator.events.templatetags.spectator_events import (
    most_seen_creators_by_works_card,
)

from hines.core import app_settings
from hines.core.utils import get_site_url

register = template.Library()


@register.simple_tag
def gravatar_url(email):
    """
    Returns the Gravatar.com for an email address.
    Or returns an empty string if the provided email is non-True.
    Docs: https://en.gravatar.com/site/implement/images/
    """
    email = email.lower().strip()
    if email:
        email_hash = md5(email.encode("utf-8")).hexdigest()
        return f"https://secure.gravatar.com/avatar/{email_hash}.jpg?d=mp&size=80"
    else:
        return ""


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
    if hasattr(context, "request") and context.request.resolver_match:
        if context.request.resolver_match.namespace:
            url_name = "{}:{}".format(
                context.request.resolver_match.namespace,
                context.request.resolver_match.url_name,
            )
        else:
            url_name = context.request.resolver_match.url_name
    return url_name


@register.filter("fieldtype")
def fieldtype(field):
    """
    For getting the type of a form field in a template.
    e.g.
        {% if field|fieldtype == "Textarea" %}
            ...
        {% endif %}
    """
    return field.field.widget.__class__.__name__


@register.simple_tag
def display_time(dt=None, show="both", granularity=0, link_to_day=False):  # noqa: FBT002
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

    # Like '%d %b %Y':
    d_fmt = app_settings.DATE_FORMAT
    # Like '%H:%M':
    t_fmt = app_settings.TIME_FORMAT
    # Like '[time] on [date]':
    dt_fmt = app_settings.DATETIME_FORMAT

    if granularity == 8:
        visible_str = "circa %s" % dt.strftime("%Y")
        stamp = dt.strftime("%Y")

    elif granularity == 6:
        visible_str = "sometime in %s" % dt.strftime("%Y")
        stamp = dt.strftime("%Y")

    elif granularity == 4:
        visible_str = "sometime in %s" % dt.strftime(
            app_settings.DATE_YEAR_MONTH_FORMAT
        )
        stamp = dt.strftime("%Y-%m")

    else:
        if show == "time":
            visible_str = dt.strftime(t_fmt)
        else:
            # Date only, or time and date:

            if link_to_day:
                url = reverse(
                    "hines:day_archive",
                    kwargs={
                        "year": dt.strftime("%Y"),
                        "month": dt.strftime("%m"),
                        "day": dt.strftime("%d"),
                    },
                )

                visible_str = (
                    f'<a href="{url}" title="All items from this day">'
                    f"{dt.strftime(d_fmt)}</a>"
                )
            else:
                visible_str = dt.strftime(d_fmt)

            if show == "both":
                # Add the time:
                visible_str = dt_fmt.replace("[date]", visible_str).replace(
                    "[time]", dt.strftime(t_fmt)
                )

        stamp = dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    return format_html(f'<time datetime="{stamp}">{visible_str}</time>')


@register.filter
def smartypants(text):
    """
    Processes the text with smartypants.
    """
    return mark_safe(_smartypants.smartypants(text))


@register.filter
def widont(text):
    """Replaces the space between the last two words in a string with ``&nbsp;``
    Works in these block tags ``(h1-h6, p, li, dd, dt)`` and also accounts for
    potential closing inline elements ``a, em, strong, span, b, i``

    From https://github.com/chrisdrackett/django-typogrify
    """
    widont_finder = re.compile(
        # must be preceeded by approved inline opening/closing tag or a nontag/nonspace:
        r"""((?:</?(?:a|em|span|strong|i|b)[^>]*>)|[^<>\s])
            # the space to replace:
            \s+
            # must be followed by non-tag non-space characters:
            ([^<>\s]+
            # optional white space:
            \s*
            # optional closing inline tags with optional white space after each:
            (</(a|em|span|strong|i|b)>\s*)*
            # end with a closing p, h1-6, li or the end of the string:
            ((</(p|h[1-6]|li|dt|dd)>)|$))
            """,
        re.VERBOSE,
    )

    output = widont_finder.sub(r"\1&nbsp;\2", text)
    return mark_safe(output)


@register.inclusion_tag("hines_core/includes/card_lastfm_scrobbles.html")
def lastfm_recent_scrobbles_card(limit=10):
    """
    Displays the most recent Scrobbles for all accounts.
    """
    more = {"text": "More at Last.fm", "url": "https://www.last.fm/user/gyford"}

    return {
        "card_title": "Recently played",
        "scrobble_list": recent_scrobbles(limit=limit),
        "more": more,
    }


@register.inclusion_tag("hines_core/includes/card_lastfm_artists.html")
def lastfm_top_artists_card(limit=10, date=None, period="day"):
    """
    Displays the most listened-to Artists for all accounts.
    """
    card_title = "Most listened-to artists"
    more = None

    if date is None:
        more = {"text": "More at Last.fm", "url": "https://www.last.fm/user/gyford"}
    else:
        if period == "day":
            pass
            # card_title += ' on this day'
        elif period == "month":
            card_title += " this month"
        elif period == "year":
            card_title += " this year"

    return {
        "card_title": card_title,
        "artist_list": top_artists(limit=limit, date=date, period=period),
        "more": more,
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
    text = re.sub(r"^<p>", '<p class="first">', text)
    return mark_safe(text)


@register.filter
def domain_urlize(value):
    """
    Returns an HTML link to the supplied URL, but only using the domain as the
    text. Strips 'www.' from the start of the domain, if present.

    e.g. if `my_url` is 'http://www.example.org/foo/' then:

        {{ my_url|domain_urlize }}

    returns:
        <a href="http://www.example.org/foo/" rel="nofollow">example.org</a>
    """
    parsed_uri = urlparse(value)
    domain = f"{parsed_uri.netloc}"

    if domain.startswith("www."):
        domain = domain[4:]

    return format_html('<a href="{}" rel="nofollow">{}</a>', value, domain)


@register.filter
def add_domain(value):
    """
    Adds 'https://www.mydomain.com' or whatever to the start of the supplied
    string, to make URLs absolute.

    value should start with a / . If it starts with 'http' then it just gets returned.
    """
    if value.startswith("http"):
        return value
    else:
        start = get_site_url()

        return f"{start}{value}"


@register.inclusion_tag("spectator_core/includes/card_chart.html")
def most_seen_directors_card(num=10):
    """
    Custom wrapper around spectator_events' most_seen_creators_by_works_card().

    This is purely so that we can group the Coen Brothers together into a
    single list item.
    """
    num = num + 1
    data = most_seen_creators_by_works_card(
        num=num, work_kind="movie", role_name="Director"
    )

    prev_creator = None
    coens = ["Joel Coen", "Ethan Coen"]
    coen_position = None

    # Original list, with the Coens occupying two adjacent positions:
    creators = data["object_list"]

    for n, creator in enumerate(creators):
        if (
            prev_creator is not None
            and prev_creator.name in coens
            and creator.name in coens
        ):
            # Both this item and the previous are Coen brothers.
            # This is the position they should both be at:
            coen_position = n
            break
        prev_creator = creator

    if coen_position is not None:
        # The Coen brothers were in the list.
        # So, get both of the Creator objects:
        coen1 = creators[coen_position - 1]
        coen2 = creators[coen_position]
        # Put them both in a list at the first position a Coen occupied:
        creators[coen_position - 1] = [coen1, coen2]
        # And delete the second position:
        del creators[coen_position]

        # Now we need to improve the positions of all subsequent people
        # because we just removed a position:
        for m, creator in enumerate(creators):
            if (
                not isinstance(creators[m], list)
                # It's not the Coens...
                and creator.chart_position > coen_position
            ):
                # And its at the same position as the Coens or after:
                creators[m].chart_position = creators[m].chart_position - 1

        data["object_list"] = creators

    # While we're here, a better title:
    data["card_title"] = "Directors by number of movies"

    return data
