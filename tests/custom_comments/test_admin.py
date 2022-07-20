from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from hines.custom_comments.admin import CustomCommentAdmin
from hines.custom_comments.factories import CommentFlagFactory, CustomCommentFactory
from hines.custom_comments.models import CustomComment
from hines.weblogs.factories import LivePostFactory


class CustomCommentAdminTestCase(TestCase):
    def test_post_title(self):
        p = LivePostFactory(title="My post title")
        c = CustomCommentFactory(post=p)
        cca = CustomCommentAdmin(CustomComment, AdminSite())
        self.assertEqual(cca.post_title(c), "My post title")

    def test_flag(self):
        "It should return the text of the most recent flag"
        c = CustomCommentFactory()
        CommentFlagFactory(comment=c, flag="This is spam")
        CommentFlagFactory(comment=c, flag="Hello")
        cca = CustomCommentAdmin(CustomComment, AdminSite())
        self.assertEqual(cca.flag(c), "Hello")

    def test_flag_none(self):
        "It should return an empty string if there are no flags."
        c = CustomCommentFactory()
        cca = CustomCommentAdmin(CustomComment, AdminSite())
        self.assertEqual(cca.flag(c), "")
