from datetime import datetime
import pytz

from django.http.response import Http404
from django.test import TestCase

from tests.core import make_datetime
from tests.core.test_views import ViewTestCase
from hines.weblogs.factories import BlogFactory, DraftPostFactory,\
        LivePostFactory
from hines.weblogs import views


class BlogDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        self.post = LivePostFactory(blog=self.blog)

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
        other_blogs_post = LivePostFactory()
        draft_post = DraftPostFactory(blog=self.blog)
        response = views.BlogDetailView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertIn('post_list', response.context_data)
        self.assertEqual(len(response.context_data['post_list']), 1)
        self.assertEqual(response.context_data['post_list'][0], self.post)

    def test_is_paginated(self):
        "It should split the posts into pages."
        # Another page's worth of posts in addition to self.post:
        LivePostFactory.create_batch(25, blog=self.blog)
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


class BlogTagDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        self.post = LivePostFactory(blog=self.blog)
        self.post.tags.add('Fish')

    def test_response_200(self):
        "It should respond with 200."
        response = views.BlogTagDetailView.as_view()(
                            self.request, blog_slug='my-blog', tag_slug='fish')
        self.assertEqual(response.status_code, 200)

    def test_response_404_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.BlogTagDetailView.as_view()(
                        self.request, blog_slug='other-blog', tag_slug='fish')

    def test_response_404_tag(self):
        "It should raise 404 if there's no tag with that slug on that Blog."
        with self.assertRaises(Http404):
            views.BlogTagDetailView.as_view()(
                        self.request, blog_slug='my-blog', tag_slug='nope')

    def test_templates(self):
        response = views.BlogTagDetailView.as_view()(
                            self.request, blog_slug='my-blog', tag_slug='fish')
        self.assertEqual(response.template_name[0],
                         'weblogs/blog_tag_detail.html')

    def test_context_post_list(self):
        "It should include the post_list, of public posts, in the context."
        # None of these should be listed:
        other_blogs_post = LivePostFactory()
        draft_post = DraftPostFactory(blog=self.blog)
        other_tag_post = LivePostFactory(blog=self.blog)
        other_tag_post.tags.add('Cats')

        response = views.BlogTagDetailView.as_view()(
                            self.request, blog_slug='my-blog', tag_slug='fish')
        self.assertIn('post_list', response.context_data)
        self.assertEqual(len(response.context_data['post_list']), 1)
        self.assertEqual(response.context_data['post_list'][0], self.post)

    def test_is_paginated(self):
        "It should split the posts into pages."
        # Another page's worth of posts in addition to self.post:
        LivePostFactory.create_batch(25, blog=self.blog, tags=['Fish',])

        # Get first page:
        response = views.BlogTagDetailView.as_view()(
                            self.request, blog_slug='my-blog', tag_slug='fish')
        self.assertEqual(len(response.context_data['post_list']), 25)

        # Get second page:
        request = self.factory.get('/fake-path/?p=2')
        response = views.BlogTagDetailView.as_view()(
                                request, blog_slug='my-blog', tag_slug='fish')
        self.assertEqual(len(response.context_data['post_list']), 1)

    def test_pagination_404(self):
        "It should raise 404 if requesting a non-existent page number."
        request = self.factory.get('/fake-path/?p=2')
        with self.assertRaises(Http404):
            views.BlogTagDetailView.as_view()(
                                request, blog_slug='my-blog', tag_slug='fish')


class BlogTagListViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog, tags=['Skate', 'Haddock', 'Cod'])
        LivePostFactory(blog=self.blog, tags=['Skate', 'Haddock',])
        LivePostFactory(blog=self.blog, tags=['Skate',])

        # These shouldn't be used in the tag list:
        DraftPostFactory(blog=self.blog, tags=['Skate',])
        LivePostFactory(tags=['Skate',])

    def test_response_200(self):
        "It should respond with 200."
        response = views.BlogTagListView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(response.status_code, 200)

    def test_response_404_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.BlogTagListView.as_view()(
                                    self.request, blog_slug='other-blog')

    def test_context_blog(self):
        response = views.BlogTagListView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)

    def test_context_tag_list(self):
        "It shouldn't include tags from draft posts or posts on other blogs."
        response = views.BlogTagListView.as_view()(
                                            self.request, blog_slug='my-blog')
        context = response.context_data
        self.assertIn('tag_list', context)
        self.assertEqual(len(context['tag_list']), 3)
        self.assertEqual(context['tag_list'][0].name, 'Skate')
        self.assertEqual(context['tag_list'][0].post_count, 3)
        self.assertEqual(context['tag_list'][1].name, 'Haddock')
        self.assertEqual(context['tag_list'][1].post_count, 2)
        self.assertEqual(context['tag_list'][2].name, 'Cod')
        self.assertEqual(context['tag_list'][2].post_count, 1)


class PostDetailViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
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

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    slug='draft-post',
                    time_published=make_datetime('2017-03-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='03',
                                                    day='01',
                                                    post_slug='draft-post')

    def test_templates(self):
        response = views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='my-post')
        self.assertEqual(response.template_name[0], 'weblogs/post_detail.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostDetailView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='02',
                                                    day='20',
                                                    post_slug='my-post')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)


class PostDayArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-02-20 12:15:00'))

    def test_response_200(self):
        "It should respond with 200."
        response = views.PostDayArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02',
                                                        day='20')
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostDayArchiveView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year='2017',
                                                    month='02',
                                                    day='20')

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching posts in that month"
        with self.assertRaises(Http404):
            views.PostDayArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='03',
                                                    day='20')

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2017-03-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostDayArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='03',
                                                    day='01')

    def test_templates(self):
        response = views.PostDayArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02',
                                                        day='20')
        self.assertEqual(response.template_name[0],
                         'weblogs/post_archive_day.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostDayArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02',
                                                        day='20')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)


class PostMonthArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-02-20 12:15:00'))

    def test_response_200(self):
        "It should respond with 200."
        response = views.PostMonthArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02')
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year='2017',
                                                    month='02')

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching posts in that month"
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='03')

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2017-03-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2017',
                                                    month='03')

    def test_templates(self):
        response = views.PostMonthArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02')
        self.assertEqual(response.template_name[0],
                         'weblogs/post_archive_month.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostMonthArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017',
                                                        month='02')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)


class PostYearArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-02-20 12:15:00'))

    def test_response_200(self):
        "It should respond with 200."
        response = views.PostYearArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017')
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year='2017')

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching posts in that month"
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2016')

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2016-01-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year='2016')

    def test_templates(self):
        response = views.PostYearArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017')
        self.assertEqual(response.template_name[0],
                         'weblogs/post_archive_year.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostYearArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year='2017')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)
