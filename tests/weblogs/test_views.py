from datetime import datetime
import pytz

from django.http.response import Http404
from django.test import TestCase

from tests.core.test_views import ViewTestCase
from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs import views


class BlogDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        BlogFactory(slug='my-blog')

    def test_response_200(self):
        "It should respond with 200."
        response = views.BlogDetailView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.BlogDetailView.as_view()(
                                        self.request, blog_slug='other-blog')

    def test_templates(self):
        response = views.BlogDetailView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(response.template_name[0], 'weblogs/blog_detail.html')


class PostDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        blog = BlogFactory(slug='my-blog')
        PostFactory(blog=blog,
                    slug='my-post',
                    time_published=datetime.strptime(
                        '2017-02-20 12:15:00', "%Y-%m-%d %H:%M:%S").replace(
                                                            tzinfo=pytz.utc))

    def test_response_200(self):
        "It should respond with 200."
        response = views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='my-post')
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostDetailView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='my-post')

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching post on that date"
        with self.assertRaises(Http404):
            views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='21',
                                                    post_slug='my-post')

    def test_response_404_invalid_post(self):
        "It should raise 404 if there's no matching post slug"
        with self.assertRaises(Http404):
            views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='OTHER-POST')

    def test_templates(self):
        response = views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='my-post')
        self.assertEqual(response.template_name[0], 'weblogs/post_detail.html')

