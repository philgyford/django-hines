from django.http.response import Http404
from django.test import RequestFactory, TestCase, override_settings

from ditto.flickr.factories import PhotoFactory
from ditto.pinboard.factories import BookmarkFactory
from ditto.twitter.factories import TweetFactory,\
        AccountFactory as TwitterAccountFactory,\
        UserFactory as TwitterUserFactory
from hines.core import views
from hines.core.utils import make_date, make_datetime
from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs.models import Post


class ViewTestCase(TestCase):
    """
    Parent class to use with all the other view test cases.
    """

    def setUp(self):
        self.factory = RequestFactory()
        # We use '/fake-path/' for all tests because not testing URLs here,
        # and the views don't care what the URL is.
        self.request = self.factory.get('/fake-path/')


class HomeViewTestCase(ViewTestCase):

    def test_response_200(self):
        "It should respond with 200."
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.template_name[0], 'hines_core/home.html')


class DayArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.today_date     = make_date('2016-08-31')
        self.today_time     = make_datetime('2016-08-31 12:00:00')
        self.tomorrow_date  = make_date('2016-09-01')
        self.tomorrow_time  = make_datetime('2016-09-01 12:00:00')
        self.yesterday_date = make_date('2016-08-30')

    def test_response_200(self):
        "It should respond with 200."
        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        self.assertEqual(response.status_code, 200)

    def test_response_future_404(self):
        "It should raise 404 if the date is in the future."
        # Apologies to the developer in September 3000 who'll find this fails.
        with self.assertRaises(Http404):
            views.DayArchiveView.as_view()(
                            self.request, year=3000, month=8, day=31)

    @override_settings(HINES_FIRST_DATE='2016-09-01')
    def test_response_old_404(self):
        "It should raise 404 if the date is before HINES_FIRST_DATE"
        with self.assertRaises(Http404):
            views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)

    def test_templates(self):
        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        self.assertEqual(response.template_name[0], 'hines_core/archive_day.html')

    def test_context_data_dates(self):
        "Should include the date and next/prev dates."
        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        self.assertIn('day', response.context_data)
        self.assertEqual(response.context_data['day'], self.today_date)
        self.assertIn('next_day', response.context_data)
        self.assertEqual(response.context_data['next_day'],
                         self.tomorrow_date)
        self.assertIn('previous_day', response.context_data)
        self.assertEqual(response.context_data['previous_day'],
                        self.yesterday_date)

    @override_settings(HINES_FIRST_DATE='2016-08-31')
    def test_context_data_dates_first(self):
        "previous_day should be False if it would be before HINES_FIRST_DATE"
        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        self.assertIn('previous_day', response.context_data)
        self.assertFalse(response.context_data['previous_day'])

    def test_context_data_blogs(self):
        "Should include public Posts from that day."
        b1 = BlogFactory(sort_order=1, slug='my-blog-1')
        # Should be included:
        p1a = PostFactory(blog=b1, status=Post.LIVE_STATUS,
                        time_published=self.today_time)
        # Draft; shouldn't be included:
        p1b = PostFactory(blog=b1, status=Post.DRAFT_STATUS,
                          time_published=self.today_time)
        # Wrong day; shouldn't be included:
        p1c = PostFactory(blog=b1, status=Post.LIVE_STATUS,
                          time_published=self.tomorrow_time)
        b2 = BlogFactory(sort_order=2, slug='my-blog-2')
        # Should be included:
        p2a = PostFactory(blog=b2, status=Post.LIVE_STATUS,
                          time_published=self.today_time)

        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        context = response.context_data
        self.assertIn('sections', context)
        sections = context['sections']
        self.assertIn('weblog_posts_my-blog-1', sections)
        self.assertIn('weblog_posts_my-blog-2', sections)
        self.assertEqual(len(sections['weblog_posts_my-blog-1']), 1)
        self.assertEqual(len(sections['weblog_posts_my-blog-2']), 1)
        self.assertEqual(sections['weblog_posts_my-blog-1'][0], p1a)
        self.assertEqual(sections['weblog_posts_my-blog-2'][0], p2a)

    def test_context_data_flickr_photos(self):
        "Should include public Photos from that day."
        photo = PhotoFactory(taken_time=self.today_time, taken_granularity=0)
        # These shouldn't appear:
        PhotoFactory(post_time=self.tomorrow_time, taken_granularity=0)
        PhotoFactory(post_time=self.today_time, taken_granularity=0,
                                                                is_private=True)
        PhotoFactory(post_time=self.today_time, taken_granularity=4)

        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        context = response.context_data
        self.assertIn('sections', context)
        sections = context['sections']
        self.assertIn('flickr_photo_list', sections)
        self.assertEqual(len(sections['flickr_photo_list']), 1)
        self.assertEqual(sections['flickr_photo_list'][0], photo)

    def test_context_data_pinboard_bookmarks(self):
        "Should include public Bookmarks from that day."
        bookmark = BookmarkFactory(post_time=self.today_time)
        # These shouldn't appear:
        BookmarkFactory(post_time=self.tomorrow_time)
        BookmarkFactory(post_time=self.today_time, is_private=True)

        response = views.DayArchiveView.as_view()(
                            self.request, year=2016, month=8, day=31)
        context = response.context_data
        self.assertIn('sections', context)
        sections = context['sections']
        self.assertIn('pinboard_bookmark_list', sections)
        self.assertEqual(len(sections['pinboard_bookmark_list']), 1)
        self.assertEqual(sections['pinboard_bookmark_list'][0], bookmark)

    # def test_context_data_twitter_favorites(self):
        # "Should include public Favorited Tweets from that day."
        # public_user = TwitterUserFactory(is_private=False)
        # private_user = TwitterUserFactory(is_private=True)
        # public_account = TwitterAccountFactory(user=public_user)
        # private_account = TwitterAccountFactory(user=private_user)

        # # Should appear:
        # favorite_tweet = TweetFactory(post_time=self.today_time)
        # public_user.favorites.add(favorite_tweet)

        # # These shouldn't appear:
        # public_user.favorites.add(
                    # TweetFactory(post_time=self.tomorrow_time))
        # private_user.favorites.add(
                    # TweetFactory(post_time=self.today_time))
        # public_user.favorites.add(
                    # TweetFactory(post_time=self.tomorrow_time,
                                 # user=private_user))

        # response = views.DayArchiveView.as_view()(
                            # self.request, year=2016, month=8, day=31)
        # context = response.context_data
        # self.assertIn('twitter_favorite_list', context)
        # self.assertEqual(len(context['twitter_favorite_list']), 1)
        # self.assertEqual(context['twitter_favorite_list'][0], favorite_tweet)

    # def test_context_data_twitter_tweets(self):
        # "Should include public Tweets (not Favorites) from that day."
        # public_user = TwitterUserFactory(is_private=False)
        # private_user = TwitterUserFactory(is_private=True)
        # public_account = TwitterAccountFactory(user=public_user)
        # private_account = TwitterAccountFactory(user=private_user)

        # tweet = TweetFactory(post_time=self.today_time,
                             # user=public_user)

        # # These shouldn't appear:
        # TweetFactory(post_time=self.tomorrow_time, user=public_user)
        # TweetFactory(post_time=self.today_time, user=private_user)
        # public_user.favorites.add(
            # TweetFactory(post_time=self.today_time))

        # response = views.DayArchiveView.as_view()(
                            # self.request, year=2016, month=8, day=31)
        # context = response.context_data
        # self.assertIn('twitter_tweet_list', context)
        # self.assertEqual(len(context['twitter_tweet_list']), 1)
        # self.assertEqual(context['twitter_tweet_list'][0], tweet)

