from unittest.mock import patch
from xml.dom import minidom

from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils.feedgenerator import rfc2822_date

from hines.core.utils import make_datetime
from hines.users.factories import UserFactory
from hines.weblogs.factories import BlogFactory, LivePostFactory
from tests import override_app_settings


class FeedTestCase(TestCase):
    """
    Borrowing some handy methods from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    def get_feed_element(self, url):
        response = self.client.get(url)
        doc = minidom.parseString(response.content)

        feed_elem = doc.getElementsByTagName("rss")
        feed = feed_elem[0]

        return feed

    def get_channel_element(self, url):
        """Handy method that returns the 'channel' tag from a feed at url.
        You can then get the items like:

            chan = self.get_channel_element('/blah/')
            items = chan.getElementsByTagName('item')
        """
        feed = self.get_feed_element(url)

        chan_elem = feed.getElementsByTagName("channel")
        chan = chan_elem[0]

        return chan

    def assertChildNodes(self, elem, expected):
        actual = set(n.nodeName for n in elem.childNodes)
        expected = set(expected)
        self.assertEqual(actual, expected)

    def assertChildNodeContent(self, elem, expected):
        for k, v in expected.items():
            try:
                self.assertEqual(
                    elem.getElementsByTagName(k)[0].firstChild.wholeText, v
                )
            except IndexError as e:
                raise IndexError("{} for '{}' and '{}'".format(e, k, v))

    def assertCategories(self, elem, expected):
        self.assertEqual(
            set(
                i.firstChild.wholeText
                for i in elem.childNodes
                if i.nodeName == "category"
            ),
            set(expected),
        )


class ExtendedFeedTestCase(FeedTestCase):
    def setUp(self):
        super().setUp()

        # To ensure our requests for the feed always use a specific domain:
        site = Site.objects.get()
        site.domain = "example.com"
        site.save()

        user = UserFactory(
            first_name="Bob", last_name="Ferris", email="bob@example.org"
        )
        blog = BlogFactory(
            name="My Blog", slug="my-blog", show_author_email_in_feed=True
        )
        LivePostFactory(
            title="My <cite>blog</cite> <b>post</b>",
            slug="my-blog-post",
            excerpt="This is <cite>my</cite> <b>excerpt</b>.",
            intro="The post intro.",
            body="This is the post <b>body</b>.\n\nOK?",
            author=user,
            blog=blog,
            time_published=make_datetime("2017-04-25 16:00:00"),
        )

    @patch("hines.weblogs.models.Post.comments_allowed", False)
    @override_app_settings(EVERYTHING_FEED_KINDS=(("blog_posts", "my-blog"),))
    def test_blog_post(self):
        """It should contain the correct data for a blog post.

        Don't want the content to be affected by whether comments are
        allowed on the Post or not for this test, so patching
        Post.comments_allowed()
        """

        channel = self.get_channel_element("/terry/feeds/everything/rss/")

        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "title": "My ‘blog’ post",
                # Can't work out how to get rid of this newline:
                "description": "This is ‘my’ excerpt.\n",
                "link": "http://example.com/terry/my-blog/2017/04/25/my-blog-post/",
                "guid": "http://example.com/terry/my-blog/2017/04/25/my-blog-post/",
                "pubDate": rfc2822_date(make_datetime("2017-04-25 16:00:00")),
                "author": "bob@example.org (Bob Ferris)",
                # Or this newline:
                "content:encoded": '<p><em>From <a href="http://example.com/terry/my-blog/">My Blog</a>.</em></p><p>The post intro.</p><p>This is the post <b>body</b>.</p><p>OK?</p>\n',  # noqa:E501
            },
        )

    @patch("hines.weblogs.models.Post.comments_allowed", True)
    @override_app_settings(EVERYTHING_FEED_KINDS=(("blog_posts", "my-blog"),))
    def test_blog_post_comments_allowed(self):
        "If comments are enabled on a Post, there should be a link in content:encoded"

        channel = self.get_channel_element("/terry/feeds/everything/rss/")

        item = channel.getElementsByTagName("item")[0]

        content = item.getElementsByTagName("content:encoded")[0].firstChild.wholeText

        self.assertEqual(
            content,
            '<p><em>From <a href="http://example.com/terry/my-blog/">My Blog</a>.</em></p><p>The post intro.</p><p>This is the post <b>body</b>.</p><p>OK?</p><hr><p><a href="http://example.com/terry/my-blog/2017/04/25/my-blog-post/#comments">Read comments or post one</a></p>\n',  # noqa: E501
        )
