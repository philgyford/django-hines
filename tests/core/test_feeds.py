from django.test import TestCase


class FeedTestCase(TestCase):
    """
    Borrowing some handy methods from
    https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
    """

    def assertChildNodes(self, elem, expected):
        actual = set(n.nodeName for n in elem.childNodes)
        expected = set(expected)
        self.assertEqual(actual, expected)

    def assertChildNodeContent(self, elem, expected):
        for k, v in expected.items():
            self.assertEqual(
                elem.getElementsByTagName(k)[0].firstChild.wholeText, v)

    def assertCategories(self, elem, expected):
        self.assertEqual(
            set(i.firstChild.wholeText for i in elem.childNodes if i.nodeName == 'category'),
            set(expected)
        )

