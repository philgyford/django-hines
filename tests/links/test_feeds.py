from ditto.pinboard.factories import AccountFactory, BookmarkFactory
from ditto.pinboard.models import Bookmark
from django.contrib.sites.models import Site
from django.utils.feedgenerator import rfc2822_date
from freezegun import freeze_time

from hines.core.utils import make_datetime
from hines.users.factories import UserFactory
from tests import override_app_settings
from tests.core.feeds import FeedTestCase


@freeze_time("2022-08-30 12:00:00", tz_offset=0)
class BookmarksFeedRSSTestCase(FeedTestCase):
    """
    Borrowing a lot from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    feed_url = "/terry/links/feeds/rss/"

    def setUp(self):
        super().setUp()
        self.user = UserFactory(
            first_name="Bob", last_name="Ferris", email="bob@example.org"
        )
        account = AccountFactory(username="bobferris")
        # 5 older LIVE posts and then 1 new post that we test in more detail:
        for _ in range(5):
            bookmark = BookmarkFactory(
                account=account,
                post_time=make_datetime("2017-04-22 15:00:00"),
            )
            bookmark.tags.set(["dogs"])

        self.bookmark2 = BookmarkFactory(
            account=account,
            title="A nice link",
            url="https://example.org",
            description="I like this",
            summary="I like this",
            post_time=make_datetime("2017-04-25 16:00:00"),
        )
        self.bookmark2.tags.set(["fish", "dogs", "cats"])
        # These shouldn't appear in our feed:
        self.private_bookmark = BookmarkFactory(account=account, is_private=True)

        # To ensure our requests for the feed always use a specific domain:
        site = Site.objects.get()
        site.domain = "example.com"
        site.save()

    def test_response_200(self):
        response = self.client.get("/terry/links/feeds/rss/")
        self.assertEqual(response.status_code, 200)

    def test_feed_element(self):
        "Testing the <rss> element"
        feed = self.get_feed_element(self.feed_url)

        self.assertEqual(
            feed.attributes["xmlns:content"].value,
            "http://purl.org/rss/1.0/modules/content/",
        )

    @override_app_settings(AUTHOR_NAME="Bob Ferris")
    def test_channel_element(self):
        "Testing the <channel> element"

        channel = self.get_channel_element(self.feed_url)

        d = Bookmark.public_objects.latest("time_modified").time_modified

        last_build_date = rfc2822_date(d)

        # We're not currently using 'ttl', 'copyright' or 'category':
        self.assertChildNodes(
            channel,
            [
                "title",
                "link",
                "description",
                "language",
                "lastBuildDate",
                "item",
                "image",
                "atom:link",
            ],
        )

        self.assertChildNodeContent(
            channel,
            {
                "title": "Recent links from Bob Ferris",
                "description": "Interesting and useful links bookmarked by Bob Ferris",
                "link": "http://example.com/terry/links/",
                "language": "en",
                "lastBuildDate": last_build_date,
            },
        )

    def test_channel_image(self):
        "Testing the <channel>'s <image> element"

        channel = self.get_channel_element(self.feed_url)

        image_el = channel.getElementsByTagName("image")[0]

        self.assertChildNodes(image_el, ["url", "title", "link"])

        self.assertChildNodeContent(
            image_el,
            {
                # This gets a hash on the end from WhiteNoise, so leaving it off
                # the test for now:
                # 'url': 'http://example.com/static/img/site_icon.jpg',
                "title": "Site icon",
                "link": "http://example.com",
            },
        )

    @override_app_settings(AUTHOR_NAME="Bob Ferris", AUTHOR_EMAIL="bob@example.com")
    def test_items(self):
        """
        Check the <item> elements
        """
        channel = self.get_channel_element(self.feed_url)
        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 6)

        # Test the content of the most recent Bookmark:

        self.assertChildNodeContent(
            items[0],
            {
                "title": "A nice link",
                "description": "I like this",
                "link": "https://example.org",
                "guid": f"http://example.com/terry/links/bobferris/{self.bookmark2.url_hash}/",
                "pubDate": rfc2822_date(self.bookmark2.post_time),
                "author": "bob@example.com (Bob Ferris)",
                "content:encoded": "I like this",
            },
        )

        self.assertCategories(items[0], ["fish", "dogs", "cats"])

        for item in items:
            self.assertChildNodes(
                item,
                [
                    "title",
                    "link",
                    "description",
                    "guid",
                    "category",
                    "pubDate",
                    "author",
                    "content:encoded",
                ],
            )
            # Assert that <guid> does not have any 'isPermaLink' attribute
            self.assertIsNone(
                item.getElementsByTagName("guid")[0].attributes.get("isPermaLink")
            )
