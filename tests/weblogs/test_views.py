from datetime import datetime
import pytz

from django.http.response import Http404
from django.test import Client, override_settings, TestCase

from hines.core.utils import make_date, make_datetime
from hines.users.models import User
from hines.weblogs.factories import (
    BlogFactory, DraftPostFactory, LivePostFactory, ScheduledPostFactory
)
from hines.weblogs import views
from tests.core.test_views import ViewTestCase
from tests import override_app_settings


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
        scheduled_post = ScheduledPostFactory(blog=self.blog)
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


class BlogArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')

    def test_response_200(self):
        "It should respond with 200."
        response = views.BlogArchiveView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.BlogArchiveView.as_view()(
                                        self.request, blog_slug='other-blog')

    def test_templates(self):
        response = views.BlogArchiveView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertEqual(response.template_name[0], 'weblogs/blog_archive.html')

    def test_context_post_list(self):
        "It should include the post_list, of public posts, in the context."
        p1 = LivePostFactory(blog=self.blog)
        p1.time_created = make_datetime('2016-01-01 12:00:00')
        p1.save()
        p2 = LivePostFactory(blog=self.blog)
        p2.time_created = make_datetime('2016-01-02 12:00:00')
        p2.save()
        p3 = LivePostFactory(blog=self.blog)
        p3.time_created = make_datetime('2016-03-01 12:00:00')
        p3.save()
        p4 = LivePostFactory(blog=self.blog)
        p4.time_created = make_datetime('2017-01-01 12:00:00')
        p4.save()

        # These shouldn't be counted:
        other_blogs_post = LivePostFactory()
        other_blogs_post.time_created = make_datetime('2016-04-01 12:00:00')
        other_blogs_post.save()
        draft_post = DraftPostFactory(blog=self.blog)
        draft_post.time_created = make_datetime('2016-05-01 12:00:00')
        draft_post.save()
        scheduled_post = ScheduledPostFactory(blog=self.blog)
        scheduled_post.time_created = make_datetime('2016-05-01 12:00:00')
        scheduled_post.save()

        response = views.BlogArchiveView.as_view()(
                                            self.request, blog_slug='my-blog')
        self.assertIn('months', response.context_data)
        months = response.context_data['months']
        self.assertEqual(len(months), 3)
        self.assertEqual(months[0], make_date('2016-01-01'))
        self.assertEqual(months[1], make_date('2016-03-01'))
        self.assertEqual(months[2], make_date('2017-01-01'))


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
        scheduled_post = ScheduledPostFactory(blog=self.blog)
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
        ScheduledPostFactory(blog=self.blog, tags=['Skate',])
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
    """
    We have to use the Client() for this view because we test whether the
    user is a superuser which requires request.user, which doesn't work with
    a RequestFactory (self.request).
    """

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        self.p = LivePostFactory(blog=self.blog,
                    slug='my-post',
                    time_published=make_datetime('2017-02-20 12:15:00'))
        self.client = Client()

    def test_response_200(self):
        "It should respond with 200."
        response = self.client.get('/terry/my-blog/2017/02/20/my-post/')
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        response = self.client.get('/terry/OTHER-BLOG/2017/02/20/my-post/')
        self.assertEqual(response.status_code, 404)

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching post on that date"
        response = self.client.get('/terry/my-blog/2017/02/21/my-post/')
        self.assertEqual(response.status_code, 404)

    def test_response_404_invalid_post(self):
        "It should raise 404 if there's no matching post slug"
        response = self.client.get('/terry/my-blog/2017/02/20/OTHER-POST/')
        self.assertEqual(response.status_code, 404)

    def test_response_404_draft_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                         slug='draft-post',
                         time_published=make_datetime('2017-02-20 12:15:00'))
        response = self.client.get('/terry/my-blog/2017/02/20/draft-post/')
        self.assertEqual(response.status_code, 404)

    def test_response_404_scheduled_status(self):
        "It should raise 404 if there's no matching published post"
        ScheduledPostFactory(blog=self.blog,
                         slug='scheduled-post',
                         time_published=make_datetime('2100-02-20 12:15:00'))
        response = self.client.get('/terry/my-blog/2100/02/20/scheduled-post/')
        self.assertEqual(response.status_code, 404)

    def test_response_preview_draft_status(self):
        "A superuser should be able to see a draft post."
        DraftPostFactory(blog=self.blog,
                         slug='draft-post',
                         time_published=make_datetime('2017-02-20 12:15:00'))
        User.objects.create_superuser('admin', 'admin@test.com', 'pass')

        self.client.login(username='admin', password='pass')
        response = self.client.get('/terry/my-blog/2017/02/20/draft-post/')

        self.assertEquals(response.status_code, 200)

    def test_response_preview_scheduled_status(self):
        "A superuser should be able to see a scheduled post."
        ScheduledPostFactory(blog=self.blog,
                         slug='scheduled-post',
                         time_published=make_datetime('2100-02-20 12:15:00'))
        User.objects.create_superuser('admin', 'admin@test.com', 'pass')

        self.client.login(username='admin', password='pass')
        response = self.client.get('/terry/my-blog/2100/02/20/scheduled-post/')

        self.assertEquals(response.status_code, 200)

    @override_app_settings(TEMPLATE_SETS=({'name':'2009', 'start': '2009-02-10', 'end': '2018-01-04'},))
    def test_templates_old(self):
        "Uses a template from the appropriate template set."
        response = self.client.get('/terry/my-blog/2017/02/20/my-post/')
        self.assertEqual(response.template_name[0],
                        'sets/2009/weblogs/post_detail.html')

    @override_app_settings(TEMPLATE_SETS=({'name':'2009', 'start': '2009-02-10', 'end': '2018-01-04'},))
    def test_templates_current(self):
        "Uses the current post_detail template"
        LivePostFactory(blog=self.blog,
                        slug='my-new-post',
                        time_published=make_datetime('2018-01-05 12:00:00'))
        response = self.client.get('/terry/my-blog/2018/01/05/my-new-post/')
        self.assertEqual(response.template_name[0], 'weblogs/post_detail.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = self.client.get('/terry/my-blog/2017/02/20/my-post/')
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)


class PostRedirectViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-02-20 12:15:00'))

    def test_redirect(self):
        response = views.PostRedirectView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year=2017,
                                                    month=2,
                                                    day=20,
                                                    post_slug='my_old_post')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                        '/terry/my-blog/2017/02/20/my-old-post/')


class PostDayArchiveViewTestCase(ViewTestCase):

    def setUp(self):
        super().setUp()
        self.blog = BlogFactory(slug='my-blog')
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-02-20 12:15:00'))

    def test_redirect(self):
        response = views.PostDayArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year=2017,
                                                        month=2,
                                                        day=20)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/terry/2017/02/20/')


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
                                                        year=2017,
                                                        month=2)
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year=2017,
                                                    month=2)

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching posts in that month"
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year=2017,
                                                    month=3)

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2017-03-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostMonthArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year=2017,
                                                    month=3)

    def test_templates(self):
        response = views.PostMonthArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year=2017,
                                                        month=2)
        self.assertEqual(response.template_name[0],
                         'weblogs/post_archive_month.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostMonthArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year=2017,
                                                        month=2)
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
                                                        year=2017)
        self.assertEqual(response.status_code, 200)

    def test_response_404_invalid_blog(self):
        "It should raise 404 if there's no Blog with that slug."
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='OTHER-BLOG',
                                                    year=2017)

    def test_response_404_invalid_date(self):
        "It should raise 404 if there's no matching posts in that month"
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year=2016)

    def test_response_404_invalid_status(self):
        "It should raise 404 if there's no matching published post"
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2016-01-01 12:15:00'))
        with self.assertRaises(Http404):
            views.PostYearArchiveView.as_view()(self.request,
                                                    blog_slug='my-blog',
                                                    year=2016)

    def test_templates(self):
        response = views.PostYearArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year=2017)
        self.assertEqual(response.template_name[0],
                         'weblogs/post_archive_year.html')

    def test_context_blog(self):
        "The blog should be in the context"
        response = views.PostYearArchiveView.as_view()(self.request,
                                                        blog_slug='my-blog',
                                                        year=2017)
        self.assertIn('blog', response.context_data)
        self.assertEqual(response.context_data['blog'], self.blog)


class RandomPhilViewTestCase(ViewTestCase):

    def test_templates_default(self):
        response = views.RandomPhilView.as_view()(self.request)
        self.assertEqual(response.template_name[0],
                         'sets/2001/weblogs/random_phil.html')

    def test_templates_2001(self):
        "Same as default"
        response = views.RandomPhilView.as_view()(self.request, set='2001')
        self.assertEqual(response.template_name[0],
                         'sets/2001/weblogs/random_phil.html')

    def test_templates_2002(self):
        response = views.RandomPhilView.as_view()(self.request, set='2002')
        self.assertEqual(response.template_name[0],
                         'sets/2002/weblogs/random_phil.html')

    def test_context(self):
        response = views.RandomPhilView.as_view()(self.request)
        context = response.context_data
        self.assertIn('idx1', context)
        self.assertEqual(context['idx1'], 1)
        self.assertIn('idx_list', context)
        self.assertIn('total_images', context)
        self.assertEqual(context['total_images'], 23)
        self.assertIn('image', context)
        self.assertIn('file', context['image'])
        self.assertIn('width', context['image'])
        self.assertIn('height', context['image'])
        self.assertIn('credit', context['image'])
        self.assertIn('caption', context['image'])
