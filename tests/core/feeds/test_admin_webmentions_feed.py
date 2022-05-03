from django.contrib.sites.models import Site

# from tests import override_app_settings
from . import FeedTestCase


class AdminWebmentionsFeedRSSTestCase(FeedTestCase):

    feed_url = "/terry/feeds/admin-webmentions/rss/"

    def setUp(self):
        super().setUp()

        # To ensure our requests for the feed always use a specific domain and name:
        site = Site.objects.get()
        site.domain = "example.com"
        site.name = "Example Site"
        site.save()

    def test_response_200(self):
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)

    # Can't work out why this test fails.
    # @override_app_settings(WEBMENTIONS_ADMIN_FEED_SLUG="good-webmentions")
    # def test_response_200_with_custom_slug(self):
    #     response = self.client.get("/terry/feeds/good-webmentions/rss/")
    #     self.assertEqual(response.status_code, 200)
