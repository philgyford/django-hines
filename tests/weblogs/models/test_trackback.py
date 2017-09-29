import datetime

from freezegun import freeze_time

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from hines.weblogs.factories import LivePostFactory, TrackbackFactory
from hines.weblogs.models import Trackback
from ...core import make_datetime


class TrackbackTestCase(TestCase):

    def test_str(self):
        tb = TrackbackFactory(title='My trackback')
        self.assertEqual(str(tb), 'My trackback')

    def test_ordering(self):
        "Reverse chronological."
        tb1 = TrackbackFactory(
                time_created=timezone.now() - datetime.timedelta(hours=1))

        tb2 = TrackbackFactory(
                time_created=timezone.now() - datetime.timedelta(hours=1))

        trackbacks = Trackback.objects.all()

        self.assertEqual(trackbacks[0], tb2)
        self.assertEqual(trackbacks[1], tb1)

    def test_unique_together(self):
        "post and url should be a unique combinatino"
        post = LivePostFactory()

        TrackbackFactory(post=post, url='http://example.com/blah.html')

        with self.assertRaises(IntegrityError):
            TrackbackFactory(post=post, url='http://example.com/blah.html')

    @freeze_time("2017-07-01 12:00:00", tz_offset=0)
    def test_save(self):
        "It should set the parent's trackback_count."
        p = LivePostFactory(trackback_count=0)
        tb = TrackbackFactory(post=p)
        p.refresh_from_db()
        self.assertEqual(p.trackback_count, 1)

    def test_save_non_public(self):
        "It shouldn't count non-public trackbacks in trackback_count."
        p = LivePostFactory(trackback_count=0)
        tb = TrackbackFactory(post=p, is_visible=False)
        p.refresh_from_db()
        self.assertEqual(p.trackback_count, 0)

    def test_delete(self):
        "It should set the parent's trackback_count."
        p = LivePostFactory(trackback_count=0)

        tb1 = TrackbackFactory(post=p)
        tb2 = TrackbackFactory(post=p)

        # Delete one trackback.
        result = tb2.delete()

        p.refresh_from_db()
        self.assertEqual(p.trackback_count, 1)

