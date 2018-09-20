from freezegun import freeze_time

from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from hines.core.utils import make_datetime
from hines.weblogs.factories import DraftPostFactory, ScheduledPostFactory
from hines.weblogs.models import Post


class PublishScheduledPostsTestCase(TestCase):

    def setUp(self):
        self.out = StringIO()

    @freeze_time("2018-05-16 12:00:00", tz_offset=0)
    def test_publishes_posts(self):
        "Should only set Scheduled posts, in the past, to LIVE."
        draft = DraftPostFactory(
                        time_published=make_datetime('2018-05-16 11:45:00'))
        scheduled_not_ready = ScheduledPostFactory(
                        time_published=make_datetime('2018-05-16 12:15:00'))
        scheduled_ready = ScheduledPostFactory(
                        time_published=make_datetime('2018-05-16 11:45:00'))

        call_command('publish_scheduled_posts', stdout=self.out)

        draft.refresh_from_db()
        scheduled_not_ready.refresh_from_db()
        scheduled_ready.refresh_from_db()

        self.assertEqual(draft.status, Post.DRAFT_STATUS)
        self.assertEqual(scheduled_not_ready.status, Post.SCHEDULED_STATUS)
        self.assertEqual(scheduled_ready.status, Post.LIVE_STATUS)

    @freeze_time("2018-05-16 12:00:00", tz_offset=0)
    def test_success_output(self):
        "Should output the correct message"
        scheduled = ScheduledPostFactory(
                        time_published=make_datetime('2018-05-16 11:45:00'))

        call_command('publish_scheduled_posts', stdout=self.out)

        self.assertIn('1 Post published', self.out.getvalue())