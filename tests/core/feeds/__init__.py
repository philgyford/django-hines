from xml.dom import minidom

from django.test import TestCase


class FeedTestCase(TestCase):
    """
    Parent class useful for testing feeds.

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
