import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from freezegun import freeze_time

from tests import override_app_settings
from hines.core.utils import make_datetime
from hines.weblogs.models import Post
from hines.weblogs.factories import (
    BlogFactory,
    DraftPostFactory,
    LivePostFactory,
    ScheduledPostFactory,
    TrackbackFactory,
)


class PostTestCase(TestCase):
    def test_str(self):
        post = LivePostFactory(title="My Blog Post")
        self.assertEqual(str(post), "My Blog Post")

    def test_ordering(self):
        publish_base = timezone.now()
        # Published later; should be third.
        p3 = LivePostFactory(
            title="B", time_published=publish_base - datetime.timedelta(hours=1)
        )
        # Most recently published; should be first:
        p1 = LivePostFactory(title="C", time_published=publish_base)
        # Published the same time as 1 but created earlier; should be second:
        p2 = LivePostFactory(title="A", time_published=publish_base)

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
        "It should add <p> and <br> tags when converting line breaks."
        post = LivePostFactory(
            html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
            intro="""<a href="http://example.org">Hello</a>.
Another line.""",
        )
        self.assertEqual(
            post.intro_html,
            '<p><a href="http://example.org">Hello</a>.<br>Another line.</p>',
        )

    def test_intro_html_markdown(self):
        "It should convert markdown to html."
        post = LivePostFactory(
            html_format=Post.MARKDOWN_FORMAT, intro="[Hello](http://example.org). *OK?*"
        )
        self.assertEqual(
            post.intro_html,
            '<p><a href="http://example.org">Hello</a>. <em>OK?</em></p>',
        )

    def test_intro_html_smartypants(self):
        post = LivePostFactory(
            html_format=Post.NO_FORMAT, intro="""This... isn't -- "special"."""
        )
        self.assertEqual(
            post.intro_html, "This&#8230; isn&#8217;t &#8212; &#8220;special&#8221;."
        )

    def test_body_html_no_format(self):
        "With no formmating, body_html should be the same as body."
        html = '<p><a href="http://example.org">Hello</a></p>'
        post = LivePostFactory(html_format=Post.NO_FORMAT, body=html)
        self.assertEqual(post.body_html, html)

    def test_body_html_convert_line_breaks(self):
        "It should add <p> and <br> tags when converting line breaks."
        post = LivePostFactory(
            html_format=Post.CONVERT_LINE_BREAKS_FORMAT,
            body="""<a href="http://example.org">Hello</a>.
Another line.""",
        )
        self.assertEqual(
            post.body_html,
            '<p><a href="http://example.org">Hello</a>.<br>Another line.</p>',
        )

    def test_body_html_markdown(self):
        "It should convert markdown to html."
        post = LivePostFactory(
            html_format=Post.MARKDOWN_FORMAT, body="[Hello](http://example.org). *OK?*"
        )
        self.assertEqual(
            post.body_html,
            '<p><a href="http://example.org">Hello</a>. <em>OK?</em></p>',
        )

    def test_body_html_smartypants(self):
        post = LivePostFactory(
            html_format=Post.NO_FORMAT, body="""This... isn't -- "special"."""
        )
        self.assertEqual(
            post.body_html, "This&#8230; isn&#8217;t &#8212; &#8220;special&#8221;."
        )

    def test_new_excerpt(self):
        "If excerpt is not set, it should be created on save."
        post = LivePostFactory(
            html_format=Post.NO_FORMAT,
            intro='<p><a href="http://example.org">Hello.</a></p>',
            body='<p>The "body" goes on for a bit so we can check the '
            'excerpt is truncated and working correctly as we would '
            'really expect it to do.</p>',
            excerpt="",
        )
        # Note: curly quotes created by Smartypants, and decoded in
        # Post.make_excerpt():
        self.assertEqual(
            post.excerpt,
            "Hello. The “body” goes on for a bit so we can check the "
            "excerpt is truncated and working correctly…",
        )

    def test_existing_excerpt(self):
        "If the excerpt it set, it isnt overwritten on save."
        post = LivePostFactory(
            intro="The intro", body="The body", excerpt="The excerpt"
        )
        self.assertEqual(post.excerpt, "The excerpt")

    @freeze_time("2017-07-01 12:00:00", tz_offset=-8)
    def test_default_time_published(self):
        "time_published should be set to now by default"
        post = DraftPostFactory()
        self.assertEqual(post.time_published, timezone.now())

    def test_time_published_does_not_change(self):
        "Re-publishing a Post doesn't change the time_published."
        # First published two days ago:
        time_published = timezone.now() - datetime.timedelta(days=2)
        post = LivePostFactory(time_published=time_published)

        # Unpublish it:
        post.status = Post.DRAFT_STATUS
        post.save()

        # Republish it:
        post.status = Post.LIVE_STATUS
        post.save()

        # Hasn't changed to now:
        self.assertEqual(post.time_published, time_published)

    def test_default_manager(self):
        "It should include posts of all statuses."
        LivePostFactory()
        DraftPostFactory()
        ScheduledPostFactory()
        posts = Post.objects.all()
        self.assertEqual(len(posts), 3)

    def test_public_posts_manager(self):
        "It should only include published posts."
        live_post = LivePostFactory()
        DraftPostFactory()
        ScheduledPostFactory()
        posts = Post.public_objects.all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], live_post)

    def test_get_absolute_url(self):
        blog = BlogFactory(slug="writing")
        post = LivePostFactory(
            blog=blog,
            slug="my-post",
            time_published=make_datetime("2017-04-03 12:00:00"),
        )
        self.assertEqual(post.get_absolute_url(), "/terry/writing/2017/04/03/my-post/")

    def test_get_next_post(self):
        "It should not return draft posts or posts from other blogs."
        blog = BlogFactory()
        post = LivePostFactory(
            blog=blog, time_published=make_datetime("2017-04-03 12:00:00")
        )
        DraftPostFactory(
            blog=blog, time_published=make_datetime("2017-04-04 12:00:00")
        )
        LivePostFactory(
            time_published=make_datetime("2017-04-04 12:00:00")
        )
        next_post = LivePostFactory(
            blog=blog, time_published=make_datetime("2017-04-05 12:00:00")
        )
        self.assertEqual(post.get_next_post(), next_post)

    def test_get_previous_post(self):
        "It should not return draft posts or posts from other blogs."
        blog = BlogFactory()
        post = LivePostFactory(
            blog=blog, time_published=make_datetime("2017-04-05 12:00:00")
        )
        DraftPostFactory(
            blog=blog, time_published=make_datetime("2017-04-04 12:00:00")
        )
        LivePostFactory(
            time_published=make_datetime("2017-04-04 12:00:00")
        )
        previous_post = LivePostFactory(
            blog=blog, time_published=make_datetime("2017-04-03 12:00:00")
        )
        self.assertEqual(post.get_previous_post(), previous_post)

    def test_tags(self):
        "Should be able to add tags."
        # Don't want to test everything about django-taggit.
        # Just make sure it's generall working on Posts.
        post = LivePostFactory()
        post.tags.add("Haddock", "Sea", "Fish")
        tags = post.get_tags()
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0].name, "Fish")
        self.assertEqual(tags[0].slug, "fish")
        self.assertEqual(tags[1].name, "Haddock")
        self.assertEqual(tags[1].slug, "haddock")
        self.assertEqual(tags[2].name, "Sea")
        self.assertEqual(tags[2].slug, "sea")

    def test_get_visible_trackbacks(self):
        "It should only return visible Trackbacks."
        post = LivePostFactory()
        visible_tb = TrackbackFactory(post=post, is_visible=True)
        TrackbackFactory(post=post, is_visible=False)

        trackbacks = post.get_visible_trackbacks()

        self.assertEqual(len(trackbacks), 1)
        self.assertEqual(trackbacks[0], visible_tb)

    def test_status_str(self):
        post = LivePostFactory()
        self.assertEqual(post.status_str, "Published")

    def test_main_image_url_none(self):
        """If there's no image in either intro_html or body_html it
        should return an empty string.
        """
        post = LivePostFactory(
            html_format=Post.NO_FORMAT, intro="<p>Hello.</p>", body="<p>Bye.</p>"
        )
        self.assertEqual(post.main_image_url, "")

    def test_main_image_url_from_intro(self):
        "It should return the URL of an image from intro_html if there is one."
        post = LivePostFactory(
            html_format=Post.NO_FORMAT,
            intro='<p>Hello. <img src="/dir/img1.jpg">. Bye.</p>',
            body='<p>Hello. <img src="/dir/img2.jpg">. Bye.</p>',
        )
        self.assertEqual(post.main_image_url, "/dir/img1.jpg")

    def test_main_image_url_from_body(self):
        "If there's no image in intro_html, it should return the first from body_html"
        post = LivePostFactory(
            html_format=Post.NO_FORMAT,
            intro="<p>Hello. Bye.</p>",
            body='<p>Hello. <img src="/dir/img1.jpg"></p><p>'
            '<img src="/dir/img2.jpg">. Bye.</p>',
        )
        self.assertEqual(post.main_image_url, "/dir/img1.jpg")

    @override_app_settings(ALLOW_COMMENTS=False)
    def test_comments_allowed_settings(self):
        "If the setting is False, should return False."
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertFalse(p.comments_allowed)

    @override_app_settings(ALLOW_COMMENTS=True)
    def test_comments_allowed_blog(self):
        "If the blog doesn't allow comments, it should return False."
        b = BlogFactory(allow_comments=False)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertFalse(p.comments_allowed)

    @override_app_settings(ALLOW_COMMENTS=True)
    def test_comments_allowed_post(self):
        "If the post doesn't allow comments, it should return False."
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=False)
        self.assertFalse(p.comments_allowed)

    @override_app_settings(ALLOW_COMMENTS=True)
    def test_comments_allowed_all_true(self):
        "If settings, blog and post are all true, it should return True"
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertTrue(p.comments_allowed)

    @override_app_settings()
    def test_comments_allowed_no_setting(self):
        "If no setting, but blog and post are true, it should return True"
        if hasattr(settings, "HINES_ALLOW_COMMENTS"):
            del settings.HINES_ALLOW_COMMENTS
        b = BlogFactory(allow_comments=True)
        p = LivePostFactory(blog=b, allow_comments=True)
        self.assertTrue(p.comments_allowed)
