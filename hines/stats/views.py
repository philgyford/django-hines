from django.http import Http404
from django.views.generic import TemplateView

from spectator.reading.utils import annual_reading_counts


class HomeView(TemplateView):
    template_name = 'stats/home.html'


class StatsView(TemplateView):
    template_name = 'stats/stats.html'

    pages = [
        {
            'slug': 'music',
            'title': 'Music',
            'charts': [
                'reading_books_per_year',
                'reading_periodicals_per_year',
            ]
        },
    ]

    def get(self, request, *args, **kwargs):
        "Ensure the slug is valid for our pages."
        slug = kwargs.get('slug', None)

        valid_slugs = [p['slug'] for p in self.pages]

        if slug in valid_slugs:
            return super().get(request, *args, **kwargs)
        else:
            raise Http404(("'{}' is not a valid slug.").format(slug))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['pages'] = self.pages

        # Include the data for the current page in addition, separately:
        for page in self.pages:
            if page['slug'] == self.kwargs.get('slug'):
                context['current_page'] = page
                break

        # Get the data for all of the charts on this page.
        context['charts'] = []
        for chart in context['current_page']['charts']:
            context['charts'].append( self.get_chart_data(chart) )

        return context

    def get_chart_data(self, chart_name):
        """
        Passed a chart_name (like 'reading_per_year') it returns a dict of
        data for its chart, including:
            'title'
            'description'
            'data' - A list of data for the chart
        """
        chart_data = {'name': chart_name,}

        data_method = getattr(self, 'get_data_{}'.format(chart_name))

        chart_data.update( data_method() )

        return chart_data

    def get_data_reading_books_per_year(self):
        return self.get_data_reading_per_year(kind='book')

    def get_data_reading_periodicals_per_year(self):
        return self.get_data_reading_per_year(kind='periodical')

    def get_data_reading_per_year(self, kind):
        """
        Used for books and periodicals.
        kind is either 'book' or 'periodical'.
        """
        chart_data = {
            'data': [],
            'title': '{}s read per year'.format(kind).capitalize(),
            'description': "Determined by date finished"
        }

        # The first years we have complete data for each kind:
        if kind == 'periodical':
            min_year = 2005
        else:
            min_year = 1998

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=kind)
        max_year = counts[-1]['year'].year

        # Make it like
        # {'2005': 37, '2006': 23'}
        counts = {str(c['year'].year):c[kind] for c in counts}

        # In case the counts have a missing year, we manually go through from
        # first to last year so we cover all years, even if there's no
        # readings.
        for year in range(min_year, max_year+1):
            syear = str(year)
            if syear in counts:
                year_data = {
                    'label': syear,
                    'value': counts[syear]
                }
            else:
                year_data = {
                    'label': syear,
                    'value': 0
                }
            chart_data['data'].append(year_data)

        return chart_data
