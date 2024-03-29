from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from hines.core.utils import make_datetime
from hines.custom_comments.factories import CustomCommentFactory
from hines.weblogs.factories import LivePostFactory
from tests import override_app_settings


class CustomCommentTestCase(TestCase):
    """
    Full tests of the comment cleaning are done in test_utils, so just
    making sure it does it generally here.
    """

    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "a"])
    def test_clean_comment_tags(self):
        p = LivePostFactory(title="Boo")
        c = CustomCommentFactory(comment="<b><i>Hi</i>", post=p)
        self.assertEqual(c.comment, "<b>Hi</b>")

    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "a"])
    def test_clean_comment_links(self):
        p = LivePostFactory()
        c = CustomCommentFactory(comment="http://foo.org", post=p)
        self.assertEqual(
            c.comment, '<a href="http://foo.org" rel="nofollow">foo.org</a>'
        )

    @freeze_time("2017-07-01 12:00:00", tz_offset=0)
    def test_save(self):
        "It should set the parent's comment_count and last_comment_time."
        p = LivePostFactory(comment_count=0, last_comment_time=None)
        CustomCommentFactory(post=p)
        p.refresh_from_db()
        self.assertEqual(p.comment_count, 1)
        self.assertEqual(p.last_comment_time, timezone.now())

    def test_save_non_public(self):
        "It shouldn't count non-public comments in comment_count etc."
        p = LivePostFactory(comment_count=0, last_comment_time=None)
        CustomCommentFactory(post=p, is_public=False)
        p.refresh_from_db()
        self.assertEqual(p.comment_count, 0)
        self.assertEqual(p.last_comment_time, None)

    def test_save_removed(self):
        "It shouldn't count removed comments in comment_count etc."
        p = LivePostFactory(comment_count=0, last_comment_time=None)
        CustomCommentFactory(post=p, is_removed=True)
        p.refresh_from_db()
        self.assertEqual(p.comment_count, 0)
        self.assertEqual(p.last_comment_time, None)

    def test_delete(self):
        "It should set the parent's comment_count and last_comment_time."
        p = LivePostFactory(comment_count=0, last_comment_time=None)

        dt1 = make_datetime("2017-09-28 12:00:00")
        dt2 = make_datetime("2017-09-29 12:00:00")
        CustomCommentFactory(post=p, submit_date=dt1)
        c2 = CustomCommentFactory(post=p, submit_date=dt2)

        # Delete the second comment.
        c2.delete()

        p.refresh_from_db()
        self.assertEqual(p.comment_count, 1)
        self.assertEqual(p.last_comment_time, dt1)
