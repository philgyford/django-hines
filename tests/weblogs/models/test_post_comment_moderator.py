from unittest.mock import patch

from django.test import RequestFactory, TestCase

from django_comments.moderation import CommentModerator

from tests import override_app_settings
from hines.custom_comments.factories import CustomCommentFactory
from hines.weblogs.factories import (
    BlogFactory,
    LivePostFactory,
)
from hines.weblogs.models import Post, PostCommentModerator


class PostCommentModeratorTestCase(TestCase):
    """
    Only testing our custom allow() method, assuming the rest is
    tested adequately by django-contrib-comments' CommentModerator.

    For each test we mock the result of the CommentModerator (the
    parent of PostCommentModerator) allow() method, so that we're
    not testing the functionality of that.
    """

    def get_moderation_result(self, blog_allow, post_allow):
        """
        Utility method for the tests.
        Create a Blog and a Post with a Comment.
        Create a new PostCommentModerator and return the result of
        calling its allow() method with that Comment and Post.

        Keyword arguments:
        blog_allow - Should the Blog.allow_comments be True or False?
        post_allow - Should the Post.allow_comments be True or False?
        """
        blog = BlogFactory(allow_comments=blog_allow)
        post = LivePostFactory(blog=blog, allow_comments=post_allow)
        comment = CustomCommentFactory(comment="Hi", post=post)
        request = RequestFactory()
        post_comment_moderator = PostCommentModerator(Post)
        return post_comment_moderator.allow(comment, post, request)

    @override_app_settings(COMMENTS_ALLOWED=True)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=None)
    @patch.object(CommentModerator, "allow")
    def test_allow_true(self, mocked_allow):
        "If everything is True, it should return True"
        mocked_allow.return_value = True
        self.assertTrue(self.get_moderation_result(blog_allow=True, post_allow=True))

    @override_app_settings(COMMENTS_ALLOWED=True)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=None)
    @patch.object(CommentModerator, "allow")
    def test_allow_parent_returns_false(self, mocked_allow):
        "If parent method returns False, so should this method."
        mocked_allow.return_value = False
        self.assertFalse(self.get_moderation_result(blog_allow=True, post_allow=True))

    @override_app_settings(COMMENTS_ALLOWED=True)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=None)
    @patch.object(CommentModerator, "allow")
    def test_allow_post_comments_allowed_false(self, mocked_allow):
        "If the Post's allow_comments setting is False, it should return False"
        mocked_allow.return_value = True
        self.assertFalse(self.get_moderation_result(blog_allow=True, post_allow=False))

    @override_app_settings(COMMENTS_ALLOWED=True)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=None)
    @patch.object(CommentModerator, "allow")
    def test_allow_blog_allow_comments_false(self, mocked_allow):
        "If the Blog's allow_comments is False, it should return False"
        mocked_allow.return_value = True
        self.assertFalse(self.get_moderation_result(blog_allow=False, post_allow=True))

    @override_app_settings(COMMENTS_ALLOWED=False)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=None)
    @patch.object(CommentModerator, "allow")
    def test_allow_settings_comments_allowed_false(self, mocked_allow):
        "If the HINES_COMMENTS_ALLOWED setting is False, it should return False"
        mocked_allow.return_value = True
        self.assertFalse(self.get_moderation_result(blog_allow=True, post_allow=True))

    @override_app_settings(COMMENTS_ALLOWED=True)
    @override_app_settings(COMMENTS_CLOSE_AFTER_DAYS=0)
    @patch.object(CommentModerator, "allow")
    def test_allow_settings_comments_closed_false(self, mocked_allow):
        """If the HINES_COMMENTS_CLOSE_AFTER_DAYS means comments aren't allowed,
        it should return False
        """
        mocked_allow.return_value = True
        self.assertFalse(self.get_moderation_result(blog_allow=True, post_allow=True))