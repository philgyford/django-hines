from xml.dom import minidom

from django.core.cache import cache
from django.test import TestCase


class FeedTestCase(TestCase):
    """
    Parent class useful for testing feeds.

    Borrowing some handy methods from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    def tearDown(self):
        super().tearDown()
        # Had problems with caches when running in development with a cache:
        cache.clear()

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

    def assertChildNodes(self, elem, expected):  # noqa: N802
        actual = set(n.nodeName for n in elem.childNodes)
        expected = set(expected)
        # print("Actual", actual)
        # print("Expected", expected)
        self.assertEqual(actual, expected)

    def assertChildNodeContent(self, elem, expected):  # noqa: N802
        for k, v in expected.items():
            try:
                self.assertEqual(
                    elem.getElementsByTagName(k)[0].firstChild.wholeText, v
                )
            except IndexError as err:
                msg = f"{err} for '{k}' and '{v}'"
                raise IndexError(msg) from err

    def assertCategories(self, elem, expected):  # noqa: N802
        self.assertEqual(
            set(
                i.firstChild.wholeText
                for i in elem.childNodes
                if i.nodeName == "category"
            ),
            set(expected),
        )
