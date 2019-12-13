from io import StringIO

from freezegun import freeze_time

from django.core.management import call_command
from django.test import TestCase

from hines.core.utils import make_datetime
from hines.weblogs.factories import DraftPostFactory, ScheduledPostFactory
from hines.weblogs.models import Post


class PublishScheduledPostsTestCase(TestCase):
    def setUp(self):
        self.out = StringIO()

    @freeze_time("2018-05-16 12:00:00", tz_offset=0)
    def test_publishes_posts(self):
        "Should only set Scheduled posts, in the past, to LIVE."
        draft = DraftPostFactory(time_published=make_datetime("2018-05-16 11:45:00"))
        scheduled_not_ready = ScheduledPostFactory(
            time_published=make_datetime("2018-05-16 12:15:00")
        )
        scheduled_ready = ScheduledPostFactory(
            time_published=make_datetime("2018-05-16 11:45:00")
        )

        call_command("publish_scheduled_posts", stdout=self.out)

        draft.refresh_from_db()
        scheduled_not_ready.refresh_from_db()
        scheduled_ready.refresh_from_db()

        self.assertEqual(draft.status, Post.Status.DRAFT)
        self.assertEqual(scheduled_not_ready.status, Post.Status.SCHEDULED)
        self.assertEqual(scheduled_ready.status, Post.Status.LIVE)

    @freeze_time("2018-05-16 12:00:00", tz_offset=0)
    def test_sets_time_published(self):
        "It should set the time_published to now"
        scheduled_ready = ScheduledPostFactory(
            time_published=make_datetime("2018-05-16 11:45:00")
        )

        call_command("publish_scheduled_posts", stdout=self.out)

        scheduled_ready.refresh_from_db()

        self.assertEqual(
            scheduled_ready.time_published, make_datetime("2018-05-16 12:00:00")
        )

    @freeze_time("2018-05-16 12:00:00", tz_offset=0)
    def test_success_output(self):
        "Should output the correct message"
        ScheduledPostFactory(time_published=make_datetime("2018-05-16 11:45:00"))

        call_command("publish_scheduled_posts", stdout=self.out)

        self.assertIn("1 Post published", self.out.getvalue())
