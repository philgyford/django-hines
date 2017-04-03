from django.test import TestCase

from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs.models import Post
from hines.weblogs.templatetags.weblogs_tags import recent_posts


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





