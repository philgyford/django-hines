from django.test import TestCase
from django.urls import resolve, reverse

from hines.weblogs import views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class WeblogsUrlsTestCase(TestCase):

    def test_blog_detail_url(self):
        self.assertEqual(
                reverse('hines:blog_detail', kwargs={'blog_slug': 'my-blog'}),
                '/phil/my-blog/')

    def test_blog_detail_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/phil/my-blog/').func.__name__,
                         views.BlogDetailView.__name__)

    def test_post_detail_url(self):
        self.assertEqual(
                reverse('hines:post_detail', kwargs={
                                'blog_slug': 'my-blog',
                                'year': '2017',
                                'month': '02',
                                'day': '20',
                                'post_slug': 'my-post'}),
                '/phil/my-blog/2017/02/20/my-post/')

    def test_post_detail_view(self):
        "Should use the correct view."
        self.assertEqual(
                resolve('/phil/my-blog/2017/02/20/my-post/').func.__name__,
                         views.PostDetailView.__name__)



