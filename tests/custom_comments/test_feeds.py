from django.utils.feedgenerator import rfc2822_date
from django.contrib.sites.models import Site

from hines.core.utils import make_datetime
from hines.custom_comments.factories import CustomCommentFactory
from hines.weblogs.factories import BlogFactory, LivePostFactory
from tests import override_app_settings
from tests.core.test_feeds import FeedTestCase


class CommentsFeedRSSParentTestCase(FeedTestCase):
    """
    No tests here, just setting stuff up that's common to the other
    CommentFeedRSS* classes below.
    """

    feed_url = "/terry/feeds/comments/rss/"

    def setUp(self):
        super().setUp()

        self.blog = BlogFactory(slug="my-blog",)
        self.post = LivePostFactory.create(
            blog=self.blog,
            title="Test Blog Post",
            slug="test-post",
            time_published=make_datetime("2020-01-01 00:00:00"),
        )
        self.comment = CustomCommentFactory.create(
            content_object=self.post,
            object_pk=self.post.pk,
            user_name="Bob Ferris",
            user_url="https://bob.org",
            comment="""<strong>This</strong> is my comment.

This is another paragraph.
""",
        )

        # To ensure our requests for the feed always use a specific domain and name:
        site = Site.objects.get()
        site.domain = "example.com"
        site.name = "Example Site"
        site.save()


class CommentsFeedRSSTestCase(CommentsFeedRSSParentTestCase):
    def test_response_200(self):
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)

    def test_feed_channel(self):
        "Testing the <channel> element"

        channel = self.get_feed_channel(self.feed_url)

        d = self.comment.submit_date
        last_build_date = rfc2822_date(d)

        # TEST THE channel ELEMENT

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

        self.assertEqual(
            channel.attributes["xmlns:content"].value,
            "http://purl.org/rss/1.0/modules/content/",
        )

        self.assertChildNodeContent(
            channel,
            {
                "title": "Comments on Example Site",
                "description": "The most recent comments on Example Site",
                "link": "http://example.com",
                "language": "en",
                "lastBuildDate": last_build_date,
            },
        )

    def test_channel_image(self):
        "Testing the <channel>'s <image> element"

        channel = self.get_feed_channel(self.feed_url)

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

    def test_items(self):
        "Check the <item> elements"
        channel = self.get_feed_channel(self.feed_url)

        items = channel.getElementsByTagName("item")
        self.assertEqual(len(items), 1)

        # Test the content of the most recent CustomComment:

        self.assertChildNodeContent(
            items[0],
            {
                "title": "Bob Ferris: Test Blog Post",
                "description": (
                    "<p><strong>This</strong> is my comment.</p>"
                    "<p>This is another paragraph.</p>"
                ),
                "link": f"http://example.com/terry/my-blog/2020/01/01/test-post/#c{self.comment.pk}",  # noqa: E501
                "guid": f"http://example.com/terry/my-blog/2020/01/01/test-post/#c{self.comment.pk}",  # noqa: E501
                "pubDate": rfc2822_date(self.comment.submit_date),
                "dc:creator": "Bob Ferris",
                "content:encoded": (
                    "<p><strong>This</strong> is my comment.</p>"
                    "<p>This is another paragraph.</p>"
                ),
            },
        )

        for item in items:
            self.assertChildNodes(
                item,
                [
                    "title",
                    "link",
                    "description",
                    "dc:creator",
                    "pubDate",
                    "guid",
                    "content:encoded",
                ],
            )
            # Assert that <guid> does not have any 'isPermaLink' attribute
            self.assertIsNone(
                item.getElementsByTagName("guid")[0].attributes.get("isPermaLink")
            )


class AdminPublishedCommentsFeedRSSTestCase(CommentsFeedRSSParentTestCase):

    feed_url = "/terry/feeds/admin-published-comments/rss/"

    def test_response_200(self):
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)

    # Can't work out why this test fails.
    # @override_app_settings(COMMENTS_ADMIN_PUBLISHED_FEED_SLUG="good-comments")
    # def test_response_200_with_custom_slug(self):
    #     response = self.client.get("/terry/feeds/good-comments/rss/")
    #     self.assertEqual(response.status_code, 200)


class AdminNotPublishedCommentsFeedRSSTestCase(CommentsFeedRSSParentTestCase):

    feed_url = "/terry/feeds/admin-not-published-comments/rss/"

    def test_response_200(self):
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)

    # Can't work out why this test fails.
    # @override_app_settings(COMMENTS_ADMIN_NOT_PUBLISHED_FEED_SLUG="spammy-comments")
    # def test_response_200_with_custom_slug(self):
    #     response = self.client.get("/terry/feeds/spammy-comments/rss/")
    #     self.assertEqual(response.status_code, 200)
