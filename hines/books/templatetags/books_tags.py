from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def linked_publication(publication):
    """
    Displays the name of the Publication, linked to its page, and adds the Authors,
    if any, each linked to their own page.
    """
    authors = ''
    if publication.authors_names_linked:
        authors = ' by %s' % publication.authors_names_linked
    return '<a href="%s"><cite>%s</cite></a>%s' % (publication.get_absolute_url(), publication, authors)


class DateSpanNode(template.Node):
    def __init__(self, start_date, start_date_granularity, end_date, end_date_granularity):
        self.start_date  = template.Variable(start_date)
        self.start_date_granularity = template.Variable(start_date_granularity)
        self.end_date  = template.Variable(end_date)
        self.end_date_granularity = template.Variable(end_date_granularity)

    def linked_date(self, date, format):
        return '<a href="%s">%s</a>' % (
                reverse(
                    'aggregator_day', 
                    kwargs={
                        'year':date.year, 
                        'month':"%02d" % date.month, 
                        'day':"%02d" % date.day,
                    }
                ),
                date.strftime(format),
            ) 
        return 
        
    def render(self, context):
        start = self.start_date.resolve(context)
        startg = self.start_date_granularity.resolve(context)
        end = self.end_date.resolve(context)
        endg = self.end_date_granularity.resolve(context)

        format = settings.DATE_FORMAT_SHORT_STRF

        span_text = ''

        if (not start) or (start == end):
            if endg == 6:
                # We only have a single year, so use that.
                span_text = end.year
            else:
                # We only have a single date, so use that.
                span_text = self.linked_date(end, format)

        elif not end:
            # We have no second date - presumably haven't/never finished this.
            span_text = "Started %s" % self.linked_date(start, format)

        else:
            # We have two different dates.
            if start.year == end.year:
                if start.month == end.month:
                    # eg '1-3 March 2006'.
                    span_text = '%s-%s' % (self.linked_date(start, '%e'), self.linked_date(end, format))
                else:
                    # eg '1 Mar - 3 Apr 2006'.
                    span_text = '%s &#8212; %s' % (self.linked_date(start, '%e %b'), self.linked_date(end, format))
            else:
                # eg '1 March 2006 - 3 April 2007'.
                span_text = '%s &#8212; %s' % (self.linked_date(start, format), self.linked_date(end, format))

        return span_text 

@register.tag
def date_span(parser, token):
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "%r tag takes exactly four arguments" % token.contents.split()[0]
    return DateSpanNode(bits[1], bits[2], bits[3], bits[4])


