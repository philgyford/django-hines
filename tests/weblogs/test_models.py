import datetime

from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone

from freezegun import freeze_time

from tests.core import make_datetime
from hines.weblogs.models import Blog, Post
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
        self.assertEqual(blog.get_absolute_url(), '/phil/writing/')


class PostTestCase(TestCase):

    def test_str(self):
        post = LivePostFactory(title='My Blog Post')
        self.assertEqual(str(post), 'My Blog Post')

    def test_ordering(self):
        publish_base = timezone.now()
        # Published later; should be third.
        p3 = LivePostFactory(title='B',
                time_published=publish_base - datetime.timedelta(hours=1))
        # Most recently published; should be first:
        p1 = LivePostFactory(title='C', time_published=publish_base)
        # Published the same time as 1 but created earlier; should be second:
        p2 = LivePostFactory(title='A', time_published=publish_base)

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
        post = LivePostFactory(html_format=Post.NO_FORMAT, intro=html)
        self.assertEqual(post.intro_html, html)

    def test_intro_html_convert_line_breaks(self):
        "It should add <p> and <br /> tags when converting line breaks."
        post = LivePostFactory(html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
                intro="""<a href="http://example.org">Hello</a>.
Another line.""")
        self.assertEqual(post.intro_html,
            '<p><a href="http://example.org">Hello</a>.<br />Another line.</p>')

    def test_intro_html_markdown(self):
        "It should convert markdown to html."
        post = LivePostFactory(html_format=Post.MARKDOWN_FORMAT,
                intro="""[Hello](http://example.org).  
*Another* line.""")
        self.assertEqual(post.intro_html,
            '<p><a href="http://example.org">Hello</a>.<br />\n<em>Another</em> line.</p>')

    def test_body_html_no_format(self):
        "With no formmating, body_html should be the same as body."
        html = '<p><a href="http://example.org">Hello</a></p>'
        post = LivePostFactory(html_format=Post.NO_FORMAT, body=html)
        self.assertEqual(post.body_html, html)

    def test_body_html_convert_line_breaks(self):
        "It should add <p> and <br /> tags when converting line breaks."
        post = LivePostFactory(html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
                body="""<a href="http://example.org">Hello</a>.
Another line.""")
        self.assertEqual(post.body_html,
            '<p><a href="http://example.org">Hello</a>.<br />Another line.</p>')

    def test_body_html_markdown(self):
        "It should convert markdown to html."
        post = LivePostFactory(html_format=Post.MARKDOWN_FORMAT,
                body="""[Hello](http://example.org).  
*Another* line.""")
        self.assertEqual(post.body_html,
            '<p><a href="http://example.org">Hello</a>.<br />\n<em>Another</em> line.</p>')

    def test_new_exceprt(self):
        "If excerpt is not set, it should be created on save."
        post = LivePostFactory(html_format=Post.NO_FORMAT,
                intro='<p><a href="http://example.org">Hello.</a></p>',
                body='<p>The body goes on for a bit so we can check the excerpt is truncated and working correctly as we would really expect it to do.</p>',
                excerpt='')
        self.assertEqual(post.excerpt,
            'Hello. The body goes on for a bit so we can check the excerpt is truncated and working correctly as…')

    def test_existing_exceprt(self):
        "If the excerpt it set, it isnt overwritten on save."
        post = LivePostFactory(intro='The intro', body='The body',
                excerpt='The excerpt')
        self.assertEqual(post.excerpt, 'The excerpt')

    @freeze_time("2017-07-01 12:00:00", tz_offset=-8)
    def test_time_published_is_set(self):
        "time_published is set when we first publish."
        post = DraftPostFactory()
        self.assertIsNone(post.time_published)
        post.status = Post.LIVE_STATUS
        post.save()
        self.assertEqual(post.time_published, timezone.now())

    def test_time_published_does_not_change(self):
        "Re-publishing a Post doesn't change the time_published."
        # First published two days ago:
        time_published = timezone.now() - datetime.timedelta(days=2)
        post = LivePostFactory(time_published=time_published)

        # Unpublish it:
        post.status=Post.DRAFT_STATUS
        post.save()

        # Republish it:
        post.status=Post.LIVE_STATUS
        post.save()
        
        # Hasn't changed to now:
        self.assertEqual(post.time_published, time_published)

    def test_default_manager(self):
        "It should include published and draft posts."
        live_post = LivePostFactory()
        draft_post = DraftPostFactory()
        posts = Post.objects.all()
        self.assertEqual(len(posts), 2)

    def test_public_posts_manager(self):
        "It should only include published posts."
        live_post = LivePostFactory()
        draft_post = DraftPostFactory()
        posts = Post.public_objects.all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], live_post)

    def test_get_absolute_url(self):
        blog = BlogFactory(slug='writing')
        post = LivePostFactory(blog=blog, slug='my-post',
                           time_published=make_datetime('2017-04-03 12:00:00'))
        self.assertEqual(post.get_absolute_url(),
                            '/phil/writing/2017/04/03/my-post/')

    def test_get_next_post(self):
        "It should not return draft posts or posts from other blogs."
        blog = BlogFactory()
        post = LivePostFactory(blog=blog,
                           time_published=make_datetime('2017-04-03 12:00:00'))
        draft_post = DraftPostFactory(blog=blog,
                           time_published=make_datetime('2017-04-04 12:00:00'))
        other_blogs_post = LivePostFactory(
                           time_published=make_datetime('2017-04-04 12:00:00'))
        next_post = LivePostFactory(blog=blog,
                           time_published=make_datetime('2017-04-05 12:00:00'))
        self.assertEqual(post.get_next_post(), next_post)

    def test_get_previous_post(self):
        "It should not return draft posts or posts from other blogs."
        blog = BlogFactory()
        post = LivePostFactory(blog=blog,
                           time_published=make_datetime('2017-04-05 12:00:00'))
        draft_post = DraftPostFactory(blog=blog,
                           time_published=make_datetime('2017-04-04 12:00:00'))
        other_blogs_post = LivePostFactory(
                           time_published=make_datetime('2017-04-04 12:00:00'))
        previous_post = LivePostFactory(blog=blog,
                           time_published=make_datetime('2017-04-03 12:00:00'))
        self.assertEqual(post.get_previous_post(), previous_post)

    def test_tags(self):
        "Should be able to add tags."
        # Don't want to test everything about django-taggit.
        # Just make sure it's generall working on Posts.
        post = LivePostFactory()
        post.tags.add('Haddock', 'Sea', 'Fish')
        tags = post.get_tags()
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0].name, 'Fish')
        self.assertEqual(tags[0].slug, 'fish')
        self.assertEqual(tags[1].name, 'Haddock')
        self.assertEqual(tags[1].slug, 'haddock')
        self.assertEqual(tags[2].name, 'Sea')
        self.assertEqual(tags[2].slug, 'sea')

    @override_settings(HINES_ALLOW_COMMENTS=False)
    def test_comments_allowed_settings(self):
        "If the setting is False, should return False."
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertFalse(p.comments_allowed)

    @override_settings(HINES_ALLOW_COMMENTS=True)
    def test_comments_allowed_blog(self):
        "If the blog doesn't allow comments, it should return False."
        b = BlogFactory(allow_comments=False)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertFalse(p.comments_allowed)

    @override_settings(HINES_ALLOW_COMMENTS=True)
    def test_comments_allowed_post(self):
        "If the post doesn't allow comments, it should return False."
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=False)
        self.assertFalse(p.comments_allowed)
        
    @override_settings(HINES_ALLOW_COMMENTS=True)
    def test_comments_allowed_all_true(self):
        "If settings, blog and post are all true, it should return True"
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertTrue(p.comments_allowed)

    @override_settings()
    def test_comments_allowed_no_setting(self):
        "If no setting, but blog and post are true, it should return True"
        if hasattr(settings, 'HINES_ALLOW_COMMENTS'):
            del settings.HINES_ALLOW_COMMENTS
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertTrue(p.comments_allowed)

