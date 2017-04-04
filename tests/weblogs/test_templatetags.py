from django.test import TestCase

from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs.models import Post
from hines.weblogs.templatetags.hines_weblogs import blog_years, recent_posts
from tests.core import make_date, make_datetime


class RecentPostsTestCase(TestCase):

    def test_blog(self):
        "It should only include posts from the specified blog."
        b1 = BlogFactory()
        b2 = BlogFactory()
        p1 = PostFactory(blog=b1, status=Post.LIVE_STATUS)
        p2 = PostFactory(blog=b2, status=Post.LIVE_STATUS)
        posts = recent_posts(blog=b1)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], p1)

    def test_public_posts(self):
        "It should only return public posts"
        blog = BlogFactory()
        live_post = PostFactory(blog=blog, status=Post.LIVE_STATUS)
        draft_post = PostFactory(blog=blog, status=Post.DRAFT_STATUS)
        posts = recent_posts(blog=blog)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], live_post)

    def test_default_num(self):
        blog = BlogFactory()
        posts = PostFactory.create_batch(6, blog=blog, status=Post.LIVE_STATUS)
        posts = recent_posts(blog=blog)
        self.assertEqual(len(posts), 5)

    def test_default_custom_num(self):
        blog = BlogFactory()
        posts = PostFactory.create_batch(7, blog=blog, status=Post.LIVE_STATUS)
        posts = recent_posts(blog=blog, num=6)
        self.assertEqual(len(posts), 6)


class BlogYearsTestCase(TestCase):

    def setUp(self):
        self.blog = BlogFactory()
        # Two published posts for this blog in 2016 and 2017:
        PostFactory(blog=self.blog, status=Post.LIVE_STATUS,
                    time_published=make_datetime('2016-03-01 12:00:00'))
        PostFactory(blog=self.blog, status=Post.LIVE_STATUS,
                    time_published=make_datetime('2017-03-01 12:00:00'))

        # This is a draft, so 2015 shouldn't be included:
        PostFactory(blog=self.blog, status=Post.DRAFT_STATUS,
                    time_published=make_datetime('2015-03-01 12:00:00'))

        # This is from a different blog, so 2014 shouldn't be included.
        PostFactory(status=Post.LIVE_STATUS,
                    time_published=make_datetime('2014-03-01 12:00:00'))
        
    def test_queryset(self):
        "Should not include draft posts or posts from other blogs."
        qs = blog_years(blog=self.blog)
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0], make_date('2016-01-01'))
        self.assertEqual(qs[1], make_date('2017-01-01'))

