from unittest.mock import patch

from django.contrib.sites.models import Site
from django.utils.feedgenerator import rfc2822_date
from freezegun import freeze_time

from hines.core.utils import make_datetime
from hines.users.factories import UserFactory
from hines.weblogs.factories import BlogFactory, DraftPostFactory, LivePostFactory
from tests.core.feeds import FeedTestCase


@freeze_time("2022-08-30 12:00:00", tz_offset=0)
class BlogPostsFeedRSSTestCase(FeedTestCase):
    """
    Borrowing a lot from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    feed_url = "/terry/my-blog/feeds/posts/rss/"

    def setUp(self):
        super().setUp()
        self.user = UserFactory(
            first_name="Bob", last_name="Ferris", email="bob@example.org"
        )
        self.blog = BlogFactory(
            name="My Blog",
            slug="my-blog",
            feed_title="My Feed Title",
            feed_description="My feed description.",
            show_author_email_in_feed=True,
        )
        # 5 older LIVE posts and then 1 new post that we test in more detail:
        LivePostFactory.create_batch(
            5,
            blog=self.blog,
            time_published=make_datetime("2017-04-22 15:00:00"),
            tags=["Dogs"],
        )
        self.post2 = LivePostFactory(
            title='Bob\'s "latest" <cite>Cited</cite> <strong>post</strong>',
            slug="my-latest-post",
            excerpt="This is <cite>my</cite> <b>excerpt</b>.",
            intro="The post intro.",
            body="This is the post <b>body</b>.\n\nOK?",
            author=self.user,
            blog=self.blog,
            time_published=make_datetime("2017-04-25 16:00:00"),
            tags=["Fish", "Dogs", "Cats"],
        )
        # These shouldn't appear in our feed:
        self.draft_post = DraftPostFactory(blog=self.blog)
        self.other_blogs_post = LivePostFactory()

        # To ensure our requests for the feed always use a specific domain:
        site = Site.objects.get()
        site.domain = "example.com"
        site.save()

    def test_response_200(self):
        response = self.client.get("/terry/my-blog/feeds/posts/rss/")
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        response = self.client.get("/terry/not-my-blog/feeds/posts/rss/")
        self.assertEqual(response.status_code, 404)

    def test_feed_element(self):
        "Testing the <rss> element"
        feed = self.get_feed_element(self.feed_url)

        self.assertEqual(
            feed.attributes["xmlns:content"].value,
            "http://purl.org/rss/1.0/modules/content/",
        )

    def test_channel_element(self):
        "Testing the <channel> element"

        channel = self.get_channel_element(self.feed_url)

        d = self.blog.public_posts.latest("time_modified").time_modified
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
                "title": "My Feed Title",
                "description": "My feed description.",
                "link": "http://example.com/terry/my-blog/",
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

    @patch("hines.weblogs.models.Post.comments_allowed", False)
    def test_items(self):
        """
        Check the <item> elements

        Don't want the content to be affected by whether comments are
        allowed on the Post or not for this test, so patching
        Post.comments_allowed()
        """
        channel = self.get_channel_element(self.feed_url)
        items = channel.getElementsByTagName("item")

        self.assertEqual(len(items), 5)

        # Test the content of the most recent Post:

        self.assertChildNodeContent(
            items[0],
            {
                "title": 'Bob\'s "latest" ‘Cited’ post',
                "description": "This is ‘my’ excerpt.",
                "link": "http://example.com/terry/my-blog/2017/04/25/my-latest-post/",
                "guid": "http://example.com/terry/my-blog/2017/04/25/my-latest-post/",
                "pubDate": rfc2822_date(self.post2.time_published),
                "author": "bob@example.org (Bob Ferris)",
                "content:encoded": "<p>The post intro.</p>\n<p>This is the post <b>body</b>.</p>\n<p>OK?</p>\n",  # noqa: E501
            },
        )

        self.assertCategories(items[0], ["Fish", "Dogs", "Cats"])

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

    @patch("hines.weblogs.models.Post.comments_allowed", True)
    def test_items_comments_allowed(self):
        "If comments are enabled on a Post, there should be a link in content:encoded"

        channel = self.get_channel_element(self.feed_url)

        item = channel.getElementsByTagName("item")[0]

        content = item.getElementsByTagName("content:encoded")[0].firstChild.wholeText

        self.assertEqual(
            content,
            '<p>The post intro.</p>\n<p>This is the post <b>body</b>.</p>\n<p>OK?</p>\n<hr><p><a href="http://example.com/terry/my-blog/2017/04/25/my-latest-post/#comments">Read comments or post one</a></p>',  # noqa: E501
        )

    def test_no_author_email(self):
        "If we don't want to show author emails, they don't appear."
        self.blog.show_author_email_in_feed = False
        self.blog.save()

        channel = self.get_channel_element(self.feed_url)

        items = channel.getElementsByTagName("item")
        self.assertEqual(len(items), 5)

        # It should have a <dc:creator> instead of <author>:

        self.assertEqual(0, len(items[0].getElementsByTagName("author")))

        self.assertEqual(
            items[0].getElementsByTagName("dc:creator")[0].firstChild.wholeText,
            "Bob Ferris",
        )
