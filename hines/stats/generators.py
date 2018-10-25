from collections import OrderedDict

from django.db.models import Count, F, Min, Max
from django.db.models.functions import TruncYear
from django.urls import reverse

from ditto.flickr.models import Photo

from spectator.events.models import Event
from spectator.reading.utils import annual_reading_counts

from ..weblogs.models import Post


# The methods in these generators should return dicts of this form:
#
# {
#   'title': 'My chart title',
#   'description: 'My optional description of the chart',
#   'data': [
#       {
#           'label': '2001',
#           'value': 37,
#           'url': '/optional/link/to/a/page/',
#       },
#       etc...
#   ]
# }


class Generator:
    """
    Parent class for all other kinds of generator.
    """

    def _queryset_to_list(self, qs, start_year=None, end_year=None, value_key='total'):
        """
        Takes a Queryset that's of this form (or years can be integers):

            [
                {
                    'year': datetime.date(2017, 1, 1),
                    'total': 37,
                },
                {
                    'year': datetime.date(2019, 1, 1),
                    'total': 42,
                },
                # etc.
            ]

        and returns it as a list in this form:

            [
                {
                    'label': '2017',
                    'value': 37,
                },
                {
                    'label': '2018',
                    'value': 0,
                },
                {
                    'label': '2019',
                    'value': 42,
                },
                # etc.
            ]

        Note:
            * It fills in any empty intermediate years with 0 values.
            * If start_year and/or end_year are provided (as integers), it
              will start and end at them, instead of the first/last QS items.
            * If the Queryset uses a different key to 'total', specify it
              as the 'value_key' parameter.
        """
        data = []

        # Put into a dict keyed by year:
        try:
            # Years are datetime.date's.
            counts = OrderedDict((c['year'].year, c[value_key]) for c in qs)
        except AttributeError:
            # Assume years are integers.
            counts = OrderedDict((c['year'], c[value_key]) for c in qs)

        if start_year is None:
            start_year = list(counts.items())[0][0]

        if end_year is None:
            end_year = list(counts.items())[-1][0]

        # In case there are years with no data, we go through ALL the possible
        # years and fill in empty years with 0 visits:
        for year in range(start_year, end_year+1):
            year_data = {
                'label': str(year),
                'value': 0,
            }
            if year in counts:
                year_data['value'] = counts[year]

            data.append(year_data)

        return data


class EventsGenerator(Generator):
    """
    For things about Spectator Events.
    """

    def __init__(self, kind):
        """
        kind is like 'cinema', 'concert', 'gig', 'theatre', etc.
        """
        self.kind = kind

    def get_per_year(self):
        kind_title = Event.get_kind_name_plural(self.kind)

        # Special cases:
        if self.kind == 'comedy':
            kind_title = 'Comedy gigs'
        elif self.kind in ['cinema', 'theatre']:
            kind_title += ' visits'

        data = {
            'data': [],
            'title': '{} per year'.format(kind_title)
        }

        qs = Event.objects.filter(kind=self.kind) \
                            .annotate(year=TruncYear('date')) \
                            .values('year') \
                            .annotate(total=Count('id')) \
                            .order_by('year')

        # We want all the event charts to span the full possible years:
        dates = Event.objects.aggregate(Min('date'), Max('date'))
        start_year = dates['date__min'].year
        end_year = dates['date__max'].year

        data['data'] = self._queryset_to_list(qs, start_year, end_year)

        return data


class FlickrGenerator(Generator):

    def get_photos_per_year(self):

        data = {
            'data': [],
            'title': 'Flickr photos per year',
            'description': 'Number of photos posted <a href="https://www.flickr.com/photos/philgyford/">on Flickr</a>.',
        }

        # Converting Photos' 'post_year' field into our required 'year':
        qs = Photo.public_objects.annotate(year=F('post_year')) \
                                    .values('year') \
                                    .annotate(total=Count('id')) \
                                    .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        return data


class ReadingGenerator(Generator):
    """
    For things about Spectator Reading.
    """

    def __init__(self, kind):
        """
        kind is either 'book' or 'periodical'.
        """
        self.kind = kind

    def get_per_year(self):
        data = {
            'data': [],
            'title': '{}s read per year'.format(self.kind).capitalize(),
            'description': "Determined by date finished."
        }

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=self.kind)

        # The first years we have complete data for each kind:
        if self.kind == 'periodical':
            start_year = 2005
        else:
            start_year = 1998

        end_year = counts[-1]['year'].year

        data['data'] = self._queryset_to_list(
                            counts, start_year, end_year, value_key=self.kind)

        # Go through and add in URLs to each year.
        for year in data['data']:
            year['url'] = reverse('spectator:reading:reading_year_archive',
                                    kwargs={'year': year['label'],
                                            'kind': '{}s'.format(self.kind)})

        return data


class StaticGenerator(Generator):
    """
    For all kinds of hard-coded data.
    """

    def get_headaches_per_year(self):
        data = {
            'data': [
                {'label': '2006', 'value': 29},
                {'label': '2007', 'value': 22},
                {'label': '2008', 'value': 18},
                {'label': '2009', 'value': 8},
                {'label': '2010', 'value': 10},
                {'label': '2011', 'value': 14},
                {'label': '2012', 'value': 12},
                {'label': '2013', 'value': 34},
                {'label': '2014', 'value': 47},
                {'label': '2015', 'value': 51},
                {'label': '2016', 'value': 59},
                {'label': '2017', 'value': 53},
            ],
            'title': 'Headaches per year',
            'description': "Those that require, or are defeated by, prescription medication."
        }

        return data


class WritingGenerator(Generator):

    def get_per_year(self):
        """
        Writing blog posts per year.
        """
        blog_slug = 'writing'

        data = {
            'title': "Writing posts per year",
            'description': 'From <a href="{}">Writing</a>.'.format(
                    reverse('weblogs:blog_detail', kwargs={'blog_slug': blog_slug})
            ),
            'data': [],
        }

        qs = Post.public_objects.filter(blog__slug=blog_slug) \
                                .annotate(year=TruncYear('time_published')) \
                                .values('year') \
                                .annotate(total=Count('id')) \
                                .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        # Go through and add URLs for each year of writing.
        for year in data['data']:
            year['url'] = reverse('weblogs:post_year_archive', kwargs={
                                    'blog_slug': blog_slug,
                                    'year': year['label'] })

        return data
