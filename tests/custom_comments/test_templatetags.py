from django.test import TestCase

from hines.core.utils import make_datetime
from hines.custom_comments.templatetags.hines_comments import (
    allowed_tags,
    clean,
    commenting_status_message,
)
from hines.weblogs.factories import BlogFactory, LivePostFactory

from tests import override_app_settings


@override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "a"])
class AllowedTagsTestCase(TestCase):
    def test_tags(self):
        self.assertEqual(allowed_tags(), ["b", "a"])


@override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "a"])
class CleanTestCase(TestCase):
    """
    Full tests of the comment cleaning are done in test_utils, so just
    making sure it does it generally here.
    """

    def test_clean_tags(self):
        self.assertEqual(clean("<b><i>Hi</i>"), "<b>Hi</b>")

    def test_clean_links(self):
        self.assertEqual(
            clean("http://foo.org"),
            '<a href="http://foo.org" rel="nofollow">foo.org</a>',
        )


class CommentingStatusMessage(TestCase):
    def test_settings_allowed_false(self):
        "If the global COMMENTS_ALLOWED setting is False the message should be returned"
        post = LivePostFactory()
        message = commenting_status_message(
            post=post, allowed=False, close_after_days=0
        )
        self.assertEqual(message, "Commenting is turned off.")

    def test_blog_allowed_false(self):
        "If the Blog's comments allowed setting is False the message should be returned"
        blog = BlogFactory(allow_comments=False)
        post = LivePostFactory(blog=blog)
        message = commenting_status_message(post=post, allowed=True, close_after_days=0)
        self.assertEqual(message, "Commenting is turned off on this blog.")

    def test_post_allowed_false(self):
        "If the Post's comments allowed setting is False the message should be returned"
        blog = BlogFactory(allow_comments=True)
        post = LivePostFactory(blog=blog, allow_comments=False)
        message = commenting_status_message(post=post, allowed=True, close_after_days=0)
        self.assertEqual(message, "Commenting is turned off for this post.")

    def test_post_too_old(self):
        """If the Post is older than the COMMENTS_CLOSE_AFTER_DAYS setting the message
        should be returned
        """
        blog = BlogFactory(allow_comments=True)
        post = LivePostFactory(
            blog=blog,
            allow_comments=True,
            time_published=make_datetime("2010-01-01 12:00:00"),
        )
        message = commenting_status_message(
            post=post, allowed=True, close_after_days=30
        )
        self.assertEqual(
            message, "Commenting is disabled on posts once they’re 30 days old."
        )

    def test_allowed(self):
        "If comments are allowed on the post, an empty string should be returned"
        blog = BlogFactory(allow_comments=True)
        post = LivePostFactory(blog=blog, allow_comments=True)
        message = commenting_status_message(
            post=post, allowed=True, close_after_days=00
        )
        self.assertEqual(message, "")
