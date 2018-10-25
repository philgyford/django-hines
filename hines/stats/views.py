from django.http import Http404
from django.views.generic import TemplateView

from .generators import (
    EventsGenerator, FlickrGenerator, ReadingGenerator, StaticGenerator,
    TwitterGenerator, WritingGenerator
)


class HomeView(TemplateView):
    template_name = 'stats/home.html'


class StatsView(TemplateView):
    template_name = 'stats/stats.html'

    pages = [
        {
            'slug': 'music',
            'title': 'Music',
            'charts': [
                'books_per_year',
                'periodicals_per_year',

                'headaches_per_year',

                'movies_per_year',
                'theatres_per_year',
                'gigs_per_year',
                'comedy_per_year',
                'museums_per_year',
                # 'concerts_per_year',
                # 'dance_per_year',
                # 'misc_events_per_year',

                'writing_per_year',

                'flickr_photos_per_year',
                'twitter_tweets_per_year',
                'twitter_favorites_per_year',
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
        Passed a chart_name (like 'books_per_year') it returns a dict of
        data for its chart, including:
            'title'
            'description'
            'data' - A list of data for the chart
        """
        chart_data = {'name': chart_name,}

        data_method = getattr(self, 'get_data_{}'.format(chart_name))

        chart_data.update( data_method() )

        return chart_data

    def get_data_books_per_year(self):
        return ReadingGenerator(kind='book').get_per_year()

    def get_data_periodicals_per_year(self):
        return ReadingGenerator(kind='periodical').get_per_year()


    def get_data_headaches_per_year(self):
        return StaticGenerator().get_headaches_per_year()


    def get_data_movies_per_year(self):
        return EventsGenerator(kind='cinema').get_per_year()

    def get_data_concerts_per_year(self):
        return EventsGenerator(kind='concert').get_per_year()

    def get_data_comedy_per_year(self):
        return EventsGenerator(kind='comedy').get_per_year()

    def get_data_dance_per_year(self):
        return EventsGenerator(kind='dance').get_per_year()

    def get_data_museums_per_year(self):
        return EventsGenerator(kind='museum').get_per_year()

    def get_data_gigs_per_year(self):
        return EventsGenerator(kind='gig').get_per_year()

    def get_data_theatres_per_year(self):
        return EventsGenerator(kind='theatre').get_per_year()

    def get_data_misc_events_per_year(self):
        return EventsGenerator(kind='misc').get_per_year()

    def get_data_writing_per_year(self):
        return WritingGenerator().get_per_year()


    def get_data_flickr_photos_per_year(self):
        return FlickrGenerator(nsid='35034346050@N01').get_photos_per_year()

    def get_data_twitter_tweets_per_year(self):
        return TwitterGenerator(screen_name='philgyford').get_tweets_per_year()

    def get_data_twitter_favorites_per_year(self):
        return TwitterGenerator(screen_name='philgyford').get_favorites_per_year()
