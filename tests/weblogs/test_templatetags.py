from django.test import TestCase

from hines.weblogs.factories import BlogFactory, DraftPostFactory,\
        LivePostFactory
from hines.weblogs.templatetags.hines_weblogs import blog_years,\
        blog_popular_tags, get_all_blogs, recent_posts
from tests.core import make_date, make_datetime


class GetAllBlogsTestCase(TestCase):

    def test_queryset(self):
        b2 = BlogFactory(sort_order=2)
        b1 = BlogFactory(sort_order=1)
        blogs = get_all_blogs()
        self.assertEqual(len(blogs), 2)
        self.assertEqual(blogs[0], b1)
        self.assertEqual(blogs[1], b2)


class RecentPostsTestCase(TestCase):

    def test_blog(self):
        "It should only include posts from the specified blog."
        b1 = BlogFactory()
        b2 = BlogFactory()
        p1 = LivePostFactory(blog=b1)
        p2 = LivePostFactory(blog=b2)
        posts = recent_posts(blog=b1)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], p1)

    def test_public_posts(self):
        "It should only return public posts"
        blog = BlogFactory()
        live_post = LivePostFactory(blog=blog)
        draft_post = DraftPostFactory(blog=blog)
        posts = recent_posts(blog=blog)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], live_post)

    def test_default_num(self):
        blog = BlogFactory()
        posts = LivePostFactory.create_batch(6, blog=blog)
        posts = recent_posts(blog=blog)
        self.assertEqual(len(posts), 5)

    def test_default_custom_num(self):
        blog = BlogFactory()
        posts = LivePostFactory.create_batch(7, blog=blog)
        posts = recent_posts(blog=blog, num=6)
        self.assertEqual(len(posts), 6)


class BlogYearsTestCase(TestCase):

    def setUp(self):
        self.blog = BlogFactory()
        # Two published posts for this blog in 2016 and 2017:
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2016-03-01 12:00:00'))
        LivePostFactory(blog=self.blog,
                    time_published=make_datetime('2017-03-01 12:00:00'))

        # This is a draft, so 2015 shouldn't be included:
        DraftPostFactory(blog=self.blog,
                    time_published=make_datetime('2015-03-01 12:00:00'))

        # This is from a different blog, so 2014 shouldn't be included.
        LivePostFactory(
                    time_published=make_datetime('2014-03-01 12:00:00'))

    def test_queryset(self):
        "Should not include draft posts or posts from other blogs."
        qs = blog_years(blog=self.blog)
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0], make_date('2016-01-01'))
        self.assertEqual(qs[1], make_date('2017-01-01'))


class BlogPopularTagsTestCase(TestCase):

    def setUp(self):
        self.blog = BlogFactory()
        fish_post_1 = LivePostFactory(blog=self.blog)
        fish_post_2 = LivePostFactory(blog=self.blog)
        fish_post_1.tags.add('Fish')
        fish_post_1.tags.add('Haddock')
        fish_post_2.tags.add('Fish')

        # Neither of these should be counted:
        draft_post = DraftPostFactory(blog=self.blog)
        draft_post.tags.add('Fish')
        other_blogs_post = LivePostFactory()
        other_blogs_post.tags.add('Fish')

    def test_queryset(self):
        "Should return the tags, in order, with post_counts."
        qs = blog_popular_tags(blog=self.blog)
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0].name, 'Fish')
        self.assertEqual(qs[0].post_count, 2)
        self.assertEqual(qs[1].name, 'Haddock')
        self.assertEqual(qs[1].post_count, 1)

    def test_queryset_num(self):
        "Should limit the number of results"
        qs = blog_popular_tags(blog=self.blog, num=1)
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0].name, 'Fish')
        self.assertEqual(qs[0].post_count, 2)

