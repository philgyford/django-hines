from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from hines.custom_comments.factories import CommentFlagFactory,\
        CustomCommentFactory
from hines.custom_comments.admin import CustomCommentAdmin
from hines.weblogs.factories import LivePostFactory
from hines.weblogs.models import Post


class CustomCommentAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()

    def test_post_title(self):
        p = LivePostFactory(title='My post title')
        c = CustomCommentFactory(post=p)
        cca = CustomCommentAdmin(c, self.site)
        self.assertEqual(cca.post_title(c), 'My post title')

    def test_flag(self):
        "It should return the text of the first flag"
        c = CustomCommentFactory()
        flag1 = CommentFlagFactory(comment=c, flag='This is spam')
        flag2 = CommentFlagFactory(comment=c, flag='Hello')
        cca = CustomCommentAdmin(c, self.site)
        self.assertEqual(cca.flag(c), 'This is spam')

    def test_flag_none(self):
        "It should return an empty string if there are no flags."
        c = CustomCommentFactory()
        cca = CustomCommentAdmin(c, self.site)
        self.assertEqual(cca.flag(c), '')

