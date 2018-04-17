from django.test import TestCase

from hines.custom_comments.templatetags.hines_comments import allowed_tags,\
        clean

from tests import override_app_settings


@override_app_settings(COMMENTS_ALLOWED_TAGS=['b', 'a',])
class AllowedTagsTestCase(TestCase):

    def test_tags(self):
        self.assertEqual(allowed_tags(), ['b', 'a',])


@override_app_settings(COMMENTS_ALLOWED_TAGS=['b', 'a',])
class CleanTestCase(TestCase):
    """
    Full tests of the comment cleaning are done in test_utils, so just
    making sure it does it generally here.
    """

    def test_clean_tags(self):
        self.assertEqual(clean('<b><i>Hi</i>'), '<b>Hi</b>')

    def test_clean_links(self):
        self.assertEqual(clean('http://foo.org'),
                '<a href="http://foo.org" rel="nofollow">foo.org</a>')
