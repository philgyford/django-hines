from datetime import datetime
import pytz

from django.http.response import Http404
from django.test import TestCase

from tests.core import make_datetime
from tests.core.test_views import ViewTestCase
from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs.models import Post
from hines.weblogs import views


class BlogDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        self.post = PostFactory(blog=self.blog, status=Post.LIVE_STATUS)

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

    def test_context_post_list(self):
        "It should include the post_list, of public posts, in the context."
        other_blogs_post = PostFactory()
        draft_post = PostFactory(blog=self.blog, status=Post.DRAFT_STATUS)
        response = views.BlogDetailView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertIn('post_list', response.context_data)
        self.assertEqual(len(response.context_data['post_list']), 1)
        self.assertEqual(response.context_data['post_list'][0], self.post)

    def test_is_paginated(self):
        "It should split the posts into pages."
        # Another page's worth of posts in addition to self.post:
        PostFactory.create_batch(25, blog=self.blog, status=Post.LIVE_STATUS)
        # Get first page:
        response = views.BlogDetailView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(len(response.context_data['post_list']), 25)

        # Get second page:
        request = self.factory.get('/fake-path/?p=2')
        response = views.BlogDetailView.as_view()(request, blog_slug='my-blog')
        self.assertEqual(len(response.context_data['post_list']), 1)

    def test_pagination_404(self):
        "It should raise 404 if requesting a non-existent page number."
        request = self.factory.get('/fake-path/?p=2')
        with self.assertRaises(Http404):
            views.BlogDetailView.as_view()(request, blog_slug='my-blog')


class PostDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        blog = BlogFactory(slug='my-blog')
        PostFactory(blog=blog,
                    slug='my-post',
                    time_published=make_datetime('2017-02-20 12:15:00'))

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

