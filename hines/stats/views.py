from django.http import Http404
from django.views.generic import TemplateView


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

        if chart_name == 'reading_books_per_year':
            chart_data['title'] = 'Reading books per year'
            chart_data['description'] = 'My description'
            chart_data['data'] = [
                {
                  'label': '2001',
                  'value': 30
                },
                {
                  'label': '2002',
                  'value': 40
                },
                {
                  'label': '2003',
                  'value': 20
                }
            ]

        return chart_data
