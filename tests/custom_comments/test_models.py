from django.test import TestCase, override_settings

from hines.custom_comments.factories import CustomCommentFactory
from hines.weblogs.factories import LivePostFactory


@override_settings(HINES_COMMENTS_ALLOWED_TAGS=['b', 'a',])
class CustomCommentTestCase(TestCase):
    """
    Full tests of the comment cleaning are done in test_utils, so just
    making sure it does it generally here.
    """

    def test_clean_comment_tags(self):
        p = LivePostFactory(title='Boo')
        c = CustomCommentFactory(comment='<b><i>Hi</i>', post=p)
        self.assertEqual(c.comment, '<b>Hi</b>')

    def test_clean_comment_links(self):
        p = LivePostFactory()
        c = CustomCommentFactory(
                            comment='http://foo.org', object_pk=p.pk)
        self.assertEqual(c.comment,
                '<a href="http://foo.org" rel="nofollow">http://foo.org</a>')

