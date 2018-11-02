from collections import OrderedDict

from django.db.models import Count, F, Min, Max
from django.db.models.functions import TruncYear
from django.urls import reverse

from ditto.flickr.models import Photo
from ditto.flickr.models import User as FlickrUser
from ditto.lastfm.models import Scrobble
from ditto.lastfm.models import Account as LastfmAccount
from ditto.pinboard.models import Bookmark
from ditto.pinboard.models import Account as PinboardAccount
from ditto.twitter.models import Tweet
from ditto.twitter.models import User as TwitterUser

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
            counts = OrderedDict(
                            (c['year'].year, c[value_key]) for c in qs)
        except AttributeError:
            # Assume years are integers.
            counts = OrderedDict((c['year'], c[value_key]) for c in qs)

        if len(counts) == 0:
            return data

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
            'title': '{}'.format(kind_title)
        }

        qs = Event.objects.filter(kind=self.kind) \
                            .annotate(year=TruncYear('date')) \
                            .values('year') \
                            .annotate(total=Count('id')) \
                            .order_by('year')

        # We want all the event charts to span the full possible years:
        dates = Event.objects.aggregate(Min('date'), Max('date'))
        try:
            start_year = dates['date__min'].year
        except AttributeError:
            start_year = None
        try:
            end_year = dates['date__max'].year
        except AttributeError:
            end_year = None

        data['data'] = self._queryset_to_list(qs, start_year, end_year)

        return data


class FlickrGenerator(Generator):

    def __init__(self, nsid):
        "nsid is like '35034346050@N01'."
        self.nsid = nsid

    def get_photos_per_year(self):
        data = {
            'data': [],
            'title': 'Flickr photos',
            'description': 'Number of photos posted <a href="https://www.flickr.com/photos/{}/">on Flickr</a> per year.'.format(self.nsid),
        }

        try:
            user = FlickrUser.objects.get(nsid=self.nsid)
        except FlickrUser.DoesNotExist:
            return data

        # Converting Photos' 'post_year' field into our required 'year':
        qs = Photo.public_objects.filter(user=user) \
                                    .annotate(year=F('post_year')) \
                                    .values('year') \
                                    .annotate(total=Count('id')) \
                                    .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        return data


class LastfmGenerator(Generator):

    def __init__(self, username):
        "username is like 'gyford'."
        self.username = username

    def get_scrobbles_per_year(self, start_year=None):
        "start_year is like 2006."

        data = {
            'data': [],
            'title': 'Tracks listened to',
            'description': 'Number of scrobbles <a href="https://www.last.fm/user/{}">on Last.fm</a> per year.'.format(
                                                                self.username),
        }

        try:
            account = LastfmAccount.objects.get(username=self.username)
        except LastfmAccount.DoesNotExist:
            return data

        # Converting Scrobbles' 'post_year' field into our required 'year':
        qs = Scrobble.public_objects.filter(account=account) \
                                    .annotate(year=F('post_year')) \
                                    .values('year') \
                                    .annotate(total=Count('id')) \
                                    .order_by('year')

        data['data'] = self._queryset_to_list(qs, start_year=start_year)

        return data


class PinboardGenerator(Generator):

    def __init__(self, username):
        "username is like 'philgyford'."
        self.username = username

    def get_bookmarks_per_year(self):
        data = {
            'data': [],
            'title': 'Links posted',
            'description': 'Number of links posted on Delicious, then <a href="https://pinboard.in/u:{}">on Pinboard</a>, per year.'.format(
                                                                self.username),
        }

        try:
            account = PinboardAccount.objects.get(username=self.username)
        except PinboardAccount.DoesNotExist:
            return data

        # Converting Bookmarks' 'post_year' field into our required 'year':
        qs = Bookmark.public_objects.filter(account=account) \
                                    .annotate(year=F('post_year')) \
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
            'title': '{}s read'.format(self.kind).capitalize(),
            'description': "Per year, determined by date finished."
        }

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=self.kind)

        # The first years we have complete data for each kind:
        if self.kind == 'periodical':
            start_year = 2005
        else:
            start_year = 1998

        try:
            end_year = counts[-1]['year'].year
        except IndexError:
            end_year = None

        data['data'] = self._queryset_to_list(
                            counts, start_year, end_year, value_key=self.kind)

        # Go through and add in URLs to each year.
        for year in data['data']:
            if year['value'] > 0:
                year['url'] = reverse('spectator:reading:reading_year_archive',
                                    kwargs={'year': year['label'],
                                            'kind': '{}s'.format(self.kind)})

        return data


class StaticGenerator(Generator):
    """
    For all kinds of hard-coded data.
    """

    def get_emails_received_per_year(self):
        # From Archive by year folders:
        personal = {
            '1995': 541,
            '1996': 792,
            '1997': 1889,
            '1998': 1702,
            '1999': 1446,
            '2000': 1898,
            '2001': 1723,
            '2002': 2719,
            '2003': 3060,
            '2004': 3255,
            '2005': 2415,
            '2006': 1813,
            '2007': 1919,
            '2008': 2464,
            '2009': 3079,
            '2010': 2423,
            '2011': 2623,
            '2012': 1523,
            '2013': 2003,
            '2014': 2145,
            '2015': 2169,
            '2016': 1996,
            '2017': 1807,
        }
        # Pepys Feedback:
        pepys = {
            '2002': 10,
            '2003': 866,
            '2004': 464,
            '2005': 554,
            '2006': 558,
            '2007': 389,
            '2008': 359,
            '2009': 253,
            '2010': 329,
            '2011': 508,
            '2012': 450,
            '2013': 266,
            '2014': 205,
            '2015': 212,
            '2016': 315,
            '2017': 251,
        }

        barbicantalk = {
            '2009': 53,
            '2010': 57,
            '2011': 44,
            '2012': 34,
            '2013': 64,
            '2014': 18,
            '2015': 12,
            '2016': 1,
            '2017': 8,
        }

        whitstillman = {
            '2002': 31,
            '2003': 29,
            '2004': 26,
            '2005': 25,
            '2006': 58,
            '2007': 60,
            '2008': 12,
            '2009': 26,
            '2010': 35,
            '2011': 40,
            '2012': 79,
            '2013': 22,
            '2014': 20,
            '2015': 16,
            '2016': 5,
            '2017': 0,
        }

        byliner = {
            '1999': 2,
            '2000': 35,
            '2001': 19,
            '2002': 33,
            '2003': 49,
            '2004': 58,
            '2005': 52,
            '2006': 78,
            '2007': 34,
            '2008': 40,
            '2009': 8,
            '2010': 49,
            '2011': 10,
        }

        # Add all the above together into a single dict:
        totals = {}

        for k, v in personal.items():
            totals[k] = v

        for k, v in pepys.items():
            totals[k] += v

        for k, v in barbicantalk.items():
            totals[k] += v

        for k, v in whitstillman.items():
            totals[k] += v

        for k, v in byliner.items():
            totals[k] += v

        data = {
            'data': [],
            'title': 'Emails received',
            'description': "Per year. Not counting: work, discussion lists, most newsletters, spam, or anything else I threw away."
        }

        # Put totals dict into correct format for charts:
        for k, v in totals.items():
            data['data'].append({
                'label': k, 'value': v,
            })

        return data

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
            'title': 'Headaches',
            'description': "Per year. Those that require, or are defeated by, prescription medication."
        }

        return data

    def get_github_contributions_per_year(self):
        # From https://github.com/philgyford
        data = {
            'data': [
                {'label': '2009', 'value': 11},
                {'label': '2010', 'value': 168},
                {'label': '2011', 'value': 97},
                {'label': '2012', 'value': 296},
                {'label': '2013', 'value': 620},
                {'label': '2014', 'value': 626},
                {'label': '2015', 'value': 1061},
                {'label': '2016', 'value': 1533},
                {'label': '2017', 'value': 1762},
            ],
            'title': 'GitHub activity',
            'description':'Contributions listed per year for <a href="https://github.com/philgyford">philgyford</a>.',
        }

        return data


class TwitterGenerator(Generator):

    def __init__(self, screen_name):
        "screen_name is like 'philgyford'."
        self.screen_name = screen_name

    def get_tweets_per_year(self):
        data = {
            'data': [],
            'title': 'Tweets posted',
            'description': 'Number of tweets posted by <a href="https://twitter.com/{}/">@{}</a> per year.'.format(
                                        self.screen_name, self.screen_name),
        }

        try:
            user = TwitterUser.objects.get(screen_name=self.screen_name)
        except TwitterUser.DoesNotExist:
            return data

        # Converting Tweets' 'post_year' field into our required 'year':
        qs = Tweet.public_tweet_objects.filter(user=user) \
                                        .annotate(year=F('post_year')) \
                                        .values('year') \
                                        .annotate(total=Count('id')) \
                                        .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        return data

    def get_favorites_per_year(self):
        data = {
            'data': [],
            'title': 'Tweets liked',
            'description': 'Number of tweets liked by <a href="https://twitter.com/{}/">@{}</a> per year.'.format(
                                        self.screen_name, self.screen_name),
        }

        try:
            user = TwitterUser.objects.get(screen_name=self.screen_name)
        except TwitterUser.DoesNotExist:
            return data

        # Converting Tweets' 'post_year' field into our required 'year':
        qs = user.favorites.annotate(year=F('post_year')) \
                            .values('year') \
                            .annotate(total=Count('id')) \
                            .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        return data


class WeblogGenerator(Generator):

    def __init__(self, blog_slug):
        "slug is the slug of the Blog, like 'writing'."
        self.blog_slug = blog_slug

    def get_posts_per_year(self):
        """
        Writing blog posts per year.
        """

        data = {
            'title': 'Writing posts',
            'description': 'Posts per year in <a href="{}">Writing</a>.'.format(
                    reverse('weblogs:blog_detail',
                            kwargs={'blog_slug': self.blog_slug})
            ),
            'data': [],
        }

        qs = Post.public_objects.filter(blog__slug=self.blog_slug) \
                                .annotate(year=TruncYear('time_published')) \
                                .values('year') \
                                .annotate(total=Count('id')) \
                                .order_by('year')

        data['data'] = self._queryset_to_list(qs)

        # Go through and add URLs for each year of writing.
        for year in data['data']:
            if year['value'] > 0:
                year['url'] = reverse('weblogs:post_year_archive', kwargs={
                                    'blog_slug': self.blog_slug,
                                    'year': year['label'] })

        return data
