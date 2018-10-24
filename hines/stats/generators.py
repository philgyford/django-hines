from django.db.models import Count, Min, Max
from django.db.models.functions import TruncYear
from django.urls import reverse

from spectator.events.models import Event
from spectator.reading.utils import annual_reading_counts

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


class EventsGenerator:
    """
    For things about Spectator Events.
    """

    def __init__(self, kind):
        """
        kind is like 'cinema', 'concert', 'gig', 'theatre', etc.
        """
        self.kind = kind

    def get_events_per_year(self):
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

        # Put into a dict keyed by str(year):
        counts = {str(c['year'].year):c['total'] for c in qs}

        # We want all the event charts to span the full possible years:
        dates = Event.objects.aggregate(Min('date'), Max('date'))
        min_year = dates['date__min'].year
        max_year = dates['date__max'].year

        # In case there are years with no data, we go through ALL the possible
        # years and fill in empty years with 0 visits:
        for year in range(min_year, max_year+1):
            syear = str(year)
            year_data = {
                'label': syear,
                'value': 0,
            }
            if syear in counts:
                year_data['value'] = counts[syear]

            data['data'].append(year_data)

        return data



class ReadingGenerator:
    """
    For things about Spectator Reading.
    """

    def __init__(self, kind):
        """
        kind is either 'book' or 'periodical'.
        """
        self.kind = kind

    def get_reading_per_year(self):
        data = {
            'data': [],
            'title': '{}s read per year'.format(self.kind).capitalize(),
            'description': "Determined by date finished."
        }

        # The first years we have complete data for each kind:
        if self.kind == 'periodical':
            min_year = 2005
        else:
            min_year = 1998

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=self.kind)
        max_year = counts[-1]['year'].year

        # Make it like
        # {'2005': 37, '2006': 23'}
        counts = {str(c['year'].year):c[self.kind] for c in counts}

        # In case the counts have a missing year, we manually go through from
        # first to last year so we cover all years, even if there's no
        # readings.
        for year in range(min_year, max_year+1):
            syear = str(year)
            year_data = {
                'label': syear,
                'value': 0
            }

            if syear in counts:
                year_data['value'] = counts[syear]
                year_data['url'] = reverse(
                                    'spectator:reading:reading_year_archive',
                                    kwargs={'year':year,
                                            'kind':'{}s'.format(self.kind)})

            data['data'].append(year_data)

        return data


class StaticGenerator:
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
