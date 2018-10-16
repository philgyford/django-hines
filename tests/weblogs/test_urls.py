from django.test import TestCase
from django.urls import resolve, reverse

from hines.weblogs import feeds, views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class WeblogsUrlsTestCase(TestCase):

    def test_blog_detail_url(self):
        self.assertEqual(
                reverse('weblogs:blog_detail', kwargs={'blog_slug': 'my-blog'}),
                '/terry/my-blog/')

    def test_blog_detail_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/terry/my-blog/').func.__name__,
                         views.BlogDetailView.__name__)


    def test_blog_archive_url(self):
        self.assertEqual(
                reverse('weblogs:blog_archive', kwargs={'blog_slug': 'my-blog'}),
                '/terry/my-blog/archive/')

    def test_blog_archive_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/terry/my-blog/archive/').func.__name__,
                         views.BlogArchiveView.__name__)


    def test_blog_feed_rss_url(self):
        self.assertEqual(
            reverse('weblogs:blog_feed_posts_rss', kwargs={'blog_slug': 'my-blog'}),
            '/terry/my-blog/feeds/posts/rss/')

    def test_blog_feed_rss_view(self):
        "Should use the correct feed object."
        self.assertIsInstance(resolve('/terry/my-blog/feeds/posts/rss/').func,
                         feeds.BlogPostsFeedRSS)


    def test_blog_tag_detail_url(self):
        self.assertEqual(
                reverse('weblogs:blog_tag_detail',
                        kwargs={'blog_slug': 'my-blog',
                                'tag_slug': 'my-tag'}),
                '/terry/my-blog/tags/my-tag/')

    def test_blog_tag_detail_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/terry/my-blog/tags/my-tag/').func.__name__,
                         views.BlogTagDetailView.__name__)


    def test_post_detail_url(self):
        self.assertEqual(
                reverse('weblogs:post_detail', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02',
                                'day': '20',
                                'post_slug': 'my-post'}),
                '/terry/my-blog/2017/02/20/my-post/')

    def test_post_detail_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/my-blog/2017/02/20/my-post/').func.__name__,
                         views.PostDetailView.__name__)


    def test_post_redirect_url(self):
        self.assertEqual(
                reverse('weblogs:post_redirect', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02',
                                'day': '20',
                                'post_slug': 'my_old_post'}),
                '/terry/my-blog/2017/02/20/my_old_post.php')

    def test_post_redirect_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve('/terry/my-blog/2017/02/20/my_old_post.php').func.__name__,
                         views.PostRedirectView.__name__)

    def test_post_redirect_index_url(self):
        self.assertEqual(
                reverse('weblogs:post_redirect_index', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02',
                                'day': '20',
                                'post_slug': 'my_old_post'}),
                '/terry/my-blog/2017/02/20/my_old_post/index.php')

    def test_post_redirect_index_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve('/terry/my-blog/2017/02/20/my_old_post/index.php').func.__name__,
                         views.PostRedirectView.__name__)

    def test_post_day_archive_url(self):
        self.assertEqual(
                reverse('weblogs:post_day_archive', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02',
                                'day': '01'}),
                '/terry/my-blog/2017/02/01/')

    def test_post_day_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/my-blog/2017/02/01/').func.__name__,
                         views.PostDayArchiveView.__name__)


    def test_post_month_archive_url(self):
        self.assertEqual(
                reverse('weblogs:post_month_archive', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02'}),
                '/terry/my-blog/2017/02/')

    def test_post_month_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/my-blog/2017/02/').func.__name__,
                         views.PostMonthArchiveView.__name__)


    def test_post_year_archive_url(self):
        self.assertEqual(
                reverse('weblogs:post_year_archive', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017'}),
                '/terry/my-blog/2017/')

    def test_post_year_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/my-blog/2017/').func.__name__,
                         views.PostYearArchiveView.__name__)


    def test_random_phil_2001_url(self):
        self.assertEqual(
                reverse('weblogs:random_phil_2001'),
                '/terry/random-phil/')

    def test_random_phil_2001_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/random-phil/').func.__name__,
                         views.RandomPhilView.__name__)

    def test_random_phil_2002_url(self):
        self.assertEqual(
                reverse('weblogs:random_phil_2002'),
                '/terry/random/')

    def test_random_phil_2002_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/terry/random/').func.__name__,
                         views.RandomPhilView.__name__)
