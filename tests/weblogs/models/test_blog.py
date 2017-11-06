from django.test import TestCase

from hines.weblogs.models import Blog
from hines.weblogs.factories import BlogFactory, DraftPostFactory,\
        LivePostFactory


class BlogTestCase(TestCase):

    def test_str(self):
        blog = BlogFactory(name='My Great Blog')
        self.assertEqual(str(blog), 'My Great Blog')

    def test_ordering(self):
        b2 = BlogFactory(sort_order=1, name='B')
        b3 = BlogFactory(sort_order=2, name='A')
        b1 = BlogFactory(sort_order=1, name='A')
        blogs = Blog.objects.all()
        self.assertEqual(blogs[0], b1)
        self.assertEqual(blogs[1], b2)
        self.assertEqual(blogs[2], b3)

    def test_posts(self):
        "Should return all posts, live or not."
        blog = BlogFactory()
        live_posts = LivePostFactory.create_batch(2, blog=blog)
        draft_post = DraftPostFactory(blog=blog)
        self.assertEqual(len(blog.posts.all()), 3)

    def test_public_posts(self):
        "Should only return live posts."
        blog = BlogFactory()
        live_posts = LivePostFactory.create_batch(2, blog=blog)
        draft_post = DraftPostFactory(blog=blog)
        self.assertEqual(len(blog.public_posts.all()), 2)

    def test_get_absolute_url(self):
        blog = BlogFactory(slug='writing')
        self.assertEqual(blog.get_absolute_url(), '/terry/writing/')

    def test_get_rss_feed_url(self):
        blog = BlogFactory(slug='writing')
        self.assertEqual(blog.get_rss_feed_url(),
                '/terry/writing/feeds/posts/rss/')

    def test_get_feed_title_default(self):
        "If there's no feed title set, the default is used."
        blog = BlogFactory(name='My Blog', feed_title='')
        self.assertEqual(blog.get_feed_title(), 'Latest posts from My Blog')

    def test_get_feed_title(self):
        "It returned feed_title if set."
        blog = BlogFactory(feed_title='A feed of great posts')
        self.assertEqual(blog.get_feed_title(), 'A feed of great posts')


