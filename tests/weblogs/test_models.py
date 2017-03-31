import datetime

from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from hines.weblogs.models import Blog, Post
from hines.weblogs.factories import BlogFactory, PostFactory


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


class PostTestCase(TestCase):

    def test_str(self):
        post = PostFactory(title='My Blog Post')
        self.assertEqual(str(post), 'My Blog Post')

    def test_ordering(self):
        publish_base = timezone.now()
        # Published later; should be third.
        p3 = PostFactory(title='B',
                time_published=publish_base - datetime.timedelta(hours=1))
        # Most recently published; should be first:
        p1 = PostFactory(title='C', time_published=publish_base)
        # Published the same time as 1 but created earlier; should be second:
        p2 = PostFactory(title='A', time_published=publish_base)

        # Adjust their automatically-generated time_createds:
        created_base = timezone.now() - datetime.timedelta(days=1)
        p1.time_created = created_base
        p1.save()
        p2.time_created = created_base - datetime.timedelta(hours=1)
        p2.save()
        p3.time_created = created_base
        p3.save()

        posts = Post.objects.all()
        self.assertEqual(posts[0], p1)
        self.assertEqual(posts[1], p2)
        self.assertEqual(posts[2], p3)

    def test_intro_html_no_format(self):
        "With no formmating, intro_html should be the same as intro."
        html = '<p><a href="http://example.org">Hello</a></p>'
        post = PostFactory(html_format=Post.NO_FORMAT, intro=html)
        self.assertEqual(post.intro_html, html)

    def test_intro_html_convert_line_breaks(self):
        "It should add <p> and <br /> tags when converting line breaks."
        post = PostFactory(html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
                intro="""<a href="http://example.org">Hello</a>.
Another line.""")
        self.assertEqual(post.intro_html,
            '<p><a href="http://example.org">Hello</a>.<br />Another line.</p>')

    def test_intro_html_markdown(self):
        "It should convert markdown to html."
        post = PostFactory(html_format=Post.MARKDOWN_FORMAT,
                intro="""[Hello](http://example.org).  
*Another* line.""")
        self.assertEqual(post.intro_html,
            '<p><a href="http://example.org">Hello</a>.<br />\n<em>Another</em> line.</p>')

    def test_body_html_no_format(self):
        "With no formmating, body_html should be the same as body."
        html = '<p><a href="http://example.org">Hello</a></p>'
        post = PostFactory(html_format=Post.NO_FORMAT, body=html)
        self.assertEqual(post.body_html, html)

    def test_body_html_convert_line_breaks(self):
        "It should add <p> and <br /> tags when converting line breaks."
        post = PostFactory(html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
                body="""<a href="http://example.org">Hello</a>.
Another line.""")
        self.assertEqual(post.body_html,
            '<p><a href="http://example.org">Hello</a>.<br />Another line.</p>')

    def test_body_html_markdown(self):
        "It should convert markdown to html."
        post = PostFactory(html_format=Post.MARKDOWN_FORMAT,
                body="""[Hello](http://example.org).  
*Another* line.""")
        self.assertEqual(post.body_html,
            '<p><a href="http://example.org">Hello</a>.<br />\n<em>Another</em> line.</p>')

    def test_new_exceprt(self):
        "If excerpt is not set, it should be created on save."
        post = PostFactory(html_format=Post.NO_FORMAT,
                intro='<p><a href="http://example.org">Hello.</a></p>',
                body='<p>The body goes on for a bit so we can check the excerpt is truncated and working correctly as we would really expect it to do.</p>',
                excerpt='')
        self.assertEqual(post.excerpt,
            'Hello. The body goes on for a bit so we can check the excerpt is truncated and working correctly as…')

    def test_existing_exceprt(self):
        "If the excerpt it set, it isnt overwritten on save."
        post = PostFactory(intro='The intro', body='The body',
                excerpt='The excerpt')
        self.assertEqual(post.excerpt, 'The excerpt')

    @freeze_time("2017-07-01 12:00:00", tz_offset=-8)
    def test_time_published_is_set(self):
        "time_published is set when we first publish."
        post = PostFactory(status=Post.DRAFT_STATUS)
        self.assertIsNone(post.time_published)
        post.status = Post.LIVE_STATUS
        post.save()
        self.assertEqual(post.time_published, timezone.now())

    def test_time_published_does_not_change(self):
        "Re-publishing a Post doesn't change the time_published."
        # First published two days ago:
        time_published = timezone.now() - datetime.timedelta(days=2)
        post = PostFactory(status=Post.LIVE_STATUS,
                time_published=time_published)

        # Unpublish it:
        post.status=Post.DRAFT_STATUS
        post.save()

        # Republish it:
        post.status=Post.LIVE_STATUS
        post.save()
        
        # Hasn't changed to now:
        self.assertEqual(post.time_published, time_published)

