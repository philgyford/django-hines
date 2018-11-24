from django.test import TestCase

from ditto.flickr.factories import UserFactory as FlickrUserFactory
from ditto.flickr.factories import PhotoFactory
from ditto.lastfm.factories import AccountFactory as LastfmAccountFactory
from ditto.lastfm.factories import ScrobbleFactory
from ditto.pinboard.factories import AccountFactory as PinboardAccountFactory
from ditto.pinboard.factories import BookmarkFactory
from ditto.twitter.factories import AccountFactory as TwitterAccountFactory
from ditto.twitter.factories import UserFactory as TwitterUserFactory
from ditto.twitter.factories import TweetFactory

from spectator.events.factories import (
    CinemaEventFactory, ComedyEventFactory, GigEventFactory,
    TheatreEventFactory
)
from spectator.reading.factories import PublicationFactory, ReadingFactory

from hines.core.utils import make_date, make_datetime
from hines.stats.generators import (
    EventsGenerator, FlickrGenerator, LastfmGenerator, PinboardGenerator,
    ReadingGenerator, StaticGenerator, TwitterGenerator, WeblogGenerator
)
from hines.weblogs.factories import (
    BlogFactory, DraftPostFactory, LivePostFactory
)


class EventsGeneratorTestCase(TestCase):

    def test_title(self):
        result = EventsGenerator('gig').get_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Gigs')

    def test_data(self):
        "General format of data is OK"
        GigEventFactory.create_batch(3, date=make_date('2018-01-01'))

        result = EventsGenerator('gig').get_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_restricts_kind(self):
        "Only counts events of the requested kind"
        GigEventFactory(date=make_date('2018-01-01'))
        CinemaEventFactory(date=make_date('2018-01-01'))

        result = EventsGenerator('gig').get_per_year()

        self.assertEqual(result['data'][0]['label'], '2018')
        # Only counts the 'gig' event:
        self.assertEqual(result['data'][0]['value'], 1)

    def test_comedy_title(self):
        "Sets custom title for Comedy kind"

        ComedyEventFactory(date=make_date('2018-01-01'))

        result = EventsGenerator('comedy').get_per_year()

        self.assertEqual(result['title'], 'Comedy gigs')

    def test_cinema_title(self):
        "Sets custom title for Cinema kind"

        CinemaEventFactory(date=make_date('2018-01-01'))

        result = EventsGenerator('cinema').get_per_year()

        self.assertEqual(result['title'], 'Cinema visits')

    def test_theatre_title(self):
        "Sets custom title for Theatre kind"

        TheatreEventFactory(date=make_date('2018-01-01'))

        result = EventsGenerator('theatre').get_per_year()

        self.assertEqual(result['title'], 'Theatre visits')

    def test_complete_years(self):
        "Should fill in all the years there are no events of this kind."
        ComedyEventFactory(date=make_date('2014-01-01'))
        GigEventFactory(date=make_date('2016-01-01'))
        ComedyEventFactory(date=make_date('2018-01-01'))

        result = EventsGenerator('gig').get_per_year()

        self.assertEqual(len(result['data']), 5)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 0},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 1},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 0},
        ])


class FlickrGeneratorTestCase(TestCase):

    def test_title_description(self):
        result = FlickrGenerator(nsid='35034346050@N01').get_photos_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Flickr photos')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Number of photos posted <a href="https://www.flickr.com/photos/35034346050@N01/">on Flickr</a> per year.')

    def test_data(self):
        "Check format of a single data element."
        user = FlickrUserFactory(nsid='35034346050@N01')
        PhotoFactory.create_batch(3,
                                user=user,
                                post_time=make_datetime('2018-01-01 12:00:00'))

        result = FlickrGenerator(nsid='35034346050@N01').get_photos_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_years(self):
        "Should include all intermediate years."
        user = FlickrUserFactory(nsid='35034346050@N01')
        PhotoFactory(user=user,
                    post_time=make_datetime('2014-01-01 12:00:00'))
        PhotoFactory.create_batch(3,
                    user=user,
                    post_time=make_datetime('2016-01-01 12:00:00'))
        PhotoFactory(user=user,
                    post_time=make_datetime('2018-01-01 12:00:00'))

        result = FlickrGenerator(nsid='35034346050@N01').get_photos_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1},
        ])


class LastfmGeneratorTestCase(TestCase):

    def test_title_description(self):
        result = LastfmGenerator(username='gyford').get_scrobbles_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Tracks listened to')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Number of scrobbles <a href="https://www.last.fm/user/gyford">on Last.fm</a> per year.')

    def test_data(self):
        account = LastfmAccountFactory(username='gyford')
        ScrobbleFactory.create_batch(3,
                                account=account,
                                post_time=make_datetime('2018-01-01 12:00:00'))

        result = LastfmGenerator(username='gyford').get_scrobbles_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_years(self):
        "Should include all intermediate years."
        account = LastfmAccountFactory(username='gyford')
        ScrobbleFactory(account=account,
                        post_time=make_datetime('2014-01-01 12:00:00'))
        ScrobbleFactory.create_batch(3,
                                account=account,
                                post_time=make_datetime('2016-01-01 12:00:00'))
        ScrobbleFactory(account=account,
                        post_time=make_datetime('2018-01-01 12:00:00'))

        result = LastfmGenerator(username='gyford').get_scrobbles_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1},
        ])


class PinboardGeneratorTestCase(TestCase):

    def test_title_description(self):
        result = PinboardGenerator(
                                username='philgyford').get_bookmarks_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Links posted')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Number of links posted on Delicious, then <a href="https://pinboard.in/u:philgyford">on Pinboard</a>, per year.')

    def test_data(self):
        account = PinboardAccountFactory(username='philgyford')
        BookmarkFactory.create_batch(3,
                                account=account,
                                post_time=make_datetime('2018-01-01 12:00:00'))

        result = PinboardGenerator(
                                username='philgyford').get_bookmarks_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_years(self):
        "Should include all intermediate years."
        account = PinboardAccountFactory(username='philgyford')
        BookmarkFactory(account=account,
                        post_time=make_datetime('2014-01-01 12:00:00'))
        BookmarkFactory.create_batch(3,
                                account=account,
                                post_time=make_datetime('2016-01-01 12:00:00'))
        BookmarkFactory(account=account,
                        post_time=make_datetime('2018-01-01 12:00:00'))

        result = PinboardGenerator(
                                username='philgyford').get_bookmarks_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1},
        ])


class ReadingGeneratorTestCase(TestCase):

    def test_book_title_description(self):
        result = ReadingGenerator(kind='book').get_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Books read')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Per year, determined by date finished.')

    def test_periodical_title(self):
        result = ReadingGenerator(kind='periodical').get_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Periodicals read')

    def test_data(self):
        "Test data returned."
        ReadingFactory.create_batch(3,
                                publication=PublicationFactory(kind='book'),
                                end_date=make_date('1998-01-01'))
        ReadingFactory(publication=PublicationFactory(kind='book'),
                                end_date=make_date('2000-01-01'))

        result = ReadingGenerator(kind='book').get_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '1998', 'value': 3, 'url': '/terry/reading/1998/books/'},
            {'label': '1999', 'value': 0},
            {'label': '2000', 'value': 1, 'url': '/terry/reading/2000/books/'},
        ])

    def test_years_book(self):
        "Books should have years from 1998."
        ReadingFactory(publication=PublicationFactory(kind='book'),
                        end_date=make_date('2008-01-01'))

        result = ReadingGenerator(kind='book').get_per_year()

        self.assertEqual(len(result['data']), 11)

    def test_years_periodicals(self):
        "Periodicas should have years from 2005."
        ReadingFactory(publication=PublicationFactory(kind='periodical'),
                        end_date=make_date('2008-01-01'))

        result = ReadingGenerator(kind='periodical').get_per_year()

        self.assertEqual(len(result['data']), 4)


class StaticGeneratorTestCase(TestCase):

    def test_diary_title_description(self):
        result = StaticGenerator().get_diary_words_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Words written in diary')
        self.assertNotIn('description', result)
        # self.assertEqual(result['description'], '')

    def test_diary_data(self):
        "Not testing the details as it's all hard-coded."
        result = StaticGenerator().get_diary_words_per_year()

        self.assertIn('data', result)
        self.assertIn('label', result['data'][0])
        self.assertIn('value', result['data'][0])

    def test_emails_title_description(self):
        result = StaticGenerator().get_emails_received_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Emails received')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Per year. Not counting: work, discussion lists, most newsletters, spam, or anything else I threw away.')

    def test_emails_data(self):
        "Not testing the details as it's all hard-coded."
        result = StaticGenerator().get_emails_received_per_year()

        self.assertIn('data', result)
        self.assertIn('label', result['data'][0])
        self.assertIn('value', result['data'][0])


    def test_headaches_title_description(self):
        result = StaticGenerator().get_headaches_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Headaches')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Per year. Those that require, or are defeated by, prescription medication.')

    def test_headaches_data(self):
        "Not testing the details as it's all hard-coded."
        result = StaticGenerator().get_headaches_per_year()

        self.assertIn('data', result)
        self.assertIn('label', result['data'][0])
        self.assertIn('value', result['data'][0])


    def test_github_title_description(self):
        result = StaticGenerator().get_github_contributions_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'GitHub activity')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Contributions listed per year for <a href="https://github.com/philgyford">philgyford</a>.')

    def test_github_data(self):
        "Not testing the details as it's all hard-coded."
        result = StaticGenerator().get_github_contributions_per_year()

        self.assertIn('data', result)
        self.assertIn('label', result['data'][0])
        self.assertIn('value', result['data'][0])


class TwitterGeneratorTestCase(TestCase):

    def test_tweets_title_description(self):
        result = TwitterGenerator(
                            screen_name='philgyford').get_tweets_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Tweets posted')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Number of tweets posted by <a href="https://twitter.com/philgyford/">@philgyford</a> per year.')

    def test_tweets_data(self):
        user = TwitterUserFactory(screen_name='philgyford', is_private=False)
        TwitterAccountFactory(user=user)
        TweetFactory.create_batch(3,
                                user=user,
                                post_time=make_datetime('2018-01-01 12:00:00'))
        # From a user without an Account; should be ignored:
        TweetFactory(post_time=make_datetime('2018-01-01 12:00:00'))

        result = TwitterGenerator(
                            screen_name='philgyford').get_tweets_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_tweets_years(self):
        "Should include all intermediate years."
        user = TwitterUserFactory(screen_name='philgyford', is_private=False)
        TwitterAccountFactory(user=user)
        TweetFactory(user=user,
                     post_time=make_datetime('2014-01-01 12:00:00'))
        TweetFactory.create_batch(3,
                                user=user,
                                post_time=make_datetime('2016-01-01 12:00:00'))
        TweetFactory(user=user,
                     post_time=make_datetime('2018-01-01 12:00:00'))
        # From a user without an Account; should be ignored:
        TweetFactory(post_time=make_datetime('2018-01-01 12:00:00'))

        result = TwitterGenerator(
                            screen_name='philgyford').get_tweets_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1},
        ])

    def test_favorites_title_description(self):
        result = TwitterGenerator(
                            screen_name='philgyford').get_favorites_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Tweets liked')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
                'Number of tweets liked by <a href="https://twitter.com/philgyford/">@philgyford</a> per year.')

    def test_favorites_data(self):
        user = TwitterUserFactory(screen_name='philgyford', is_private=False)
        account = TwitterAccountFactory(user=user)
        user.favorites.add(TweetFactory(
                            post_time=make_datetime('2018-01-01 12:00:00')))
        user.favorites.add(TweetFactory(
                            post_time=make_datetime('2018-02-01 12:00:00')))
        user.favorites.add(TweetFactory(
                            post_time=make_datetime('2018-03-01 12:00:00')))

        # Not favorited; shouldn't be counted:
        TweetFactory(post_time=make_datetime('2018-01-01 12:00:00'))

        result = TwitterGenerator(
                            screen_name='philgyford').get_favorites_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)

    def test_favorites_years(self):
        "Should include all intermediate years."
        user = TwitterUserFactory(screen_name='philgyford', is_private=False)
        account = TwitterAccountFactory(user=user)
        user.favorites.add(TweetFactory(
                             post_time=make_datetime('2014-01-01 12:00:00')))
        user.favorites.add(TweetFactory(
                             post_time=make_datetime('2016-01-01 12:00:00')))
        user.favorites.add(TweetFactory(
                             post_time=make_datetime('2016-02-01 12:00:00')))
        user.favorites.add(TweetFactory(
                             post_time=make_datetime('2016-03-01 12:00:00')))
        user.favorites.add(TweetFactory(
                             post_time=make_datetime('2018-01-01 12:00:00')))

        # Not favorited; shouldn't be counted:
        TweetFactory(post_time=make_datetime('2018-01-01 12:00:00'))

        result = TwitterGenerator(
                            screen_name='philgyford').get_favorites_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1},
        ])


class WeblogGeneratorTestCase(TestCase):

    def test_title_description(self):
        result = WeblogGenerator(blog_slug='writing').get_posts_per_year()

        self.assertIn('title', result)
        self.assertEqual(result['title'], 'Writing posts')
        self.assertIn('description', result)
        self.assertEqual(result['description'],
            'Posts per year in <a href="/terry/writing/">Writing</a>.')

    def test_data(self):
        "Not testing the details as it's all hard-coded."
        blog = BlogFactory(slug='writing')
        LivePostFactory.create_batch(3,
                        blog=blog,
                        time_published=make_datetime('2018-01-01 12:00:00'))

        result = WeblogGenerator(blog_slug='writing').get_posts_per_year()

        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['label'], '2018')
        self.assertEqual(result['data'][0]['value'], 3)
        self.assertEqual(result['data'][0]['url'], '/terry/writing/2018/')

    def test_years(self):
        "Should include all intermediate years."
        blog = BlogFactory(slug='writing')
        LivePostFactory(blog=blog,
                        time_published=make_datetime('2014-01-01 12:00:00'))
        LivePostFactory.create_batch(3,
                        blog=blog,
                        time_published=make_datetime('2016-01-01 12:00:00'))
        LivePostFactory(blog=blog,
                        time_published=make_datetime('2018-01-01 12:00:00'))

        # Shouldn't be counted:
        LivePostFactory(time_published=make_datetime('2018-01-01 12:00:00'))
        DraftPostFactory(blog=blog,
                        time_published=make_datetime('2018-01-01 12:00:00'))

        result = WeblogGenerator(blog_slug='writing').get_posts_per_year()

        self.assertIn('data', result)
        self.assertEqual(result['data'], [
            {'label': '2014', 'value': 1, 'url': '/terry/writing/2014/'},
            {'label': '2015', 'value': 0},
            {'label': '2016', 'value': 3, 'url': '/terry/writing/2016/'},
            {'label': '2017', 'value': 0},
            {'label': '2018', 'value': 1, 'url': '/terry/writing/2018/'},
        ])
