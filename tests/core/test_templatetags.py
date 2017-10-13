from unittest.mock import patch

from django.test import TestCase

from hines.core.templatetags.hines_core import get_item, display_time,\
        smartypants
from hines.core.utils import make_datetime


class GetItemTestCase(TestCase):

    def test_returns_value(self):
        ages = {'bob': 37,}
        self.assertEqual(get_item(ages, 'bob'), 37)

    def test_returns_None(self):
        ages = {'bob': 37,}
        self.assertIsNone(get_item(ages, 'amy'))


class DisplayTimeTestCase(TestCase):

    def test_returns_datetime_by_default(self):
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56')),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14&nbsp;Aug&nbsp;2015</time>'
        )

    def test_returns_datetime(self):
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='both'),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14&nbsp;Aug&nbsp;2015</time>'
        )

    def test_returns_date(self):
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='date'),
            '<time datetime="2015-08-14 13:34:56">14&nbsp;Aug&nbsp;2015</time>'
        )

    def test_returns_time(self):
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='time'),
            '<time datetime="2015-08-14 13:34:56">13:34</time>'
        )

    @patch('hines.core.templatetags.hines_core.reverse')
    def test_returns_datetime_with_link(self, reverse):
        reverse.return_value = '/2015/08/14/'
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='both', link_to_day=True),
            '<time datetime="2015-08-14 13:34:56">13:34 on <a href="/2015/08/14/" title="All items from this day">14&nbsp;Aug&nbsp;2015</a></time>'
        )

    @patch('hines.core.templatetags.hines_core.reverse')
    def test_returns_date_with_link(self, reverse):
        reverse.return_value = '/2015/08/14/'
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='date', link_to_day=True),
            '<time datetime="2015-08-14 13:34:56"><a href="/2015/08/14/" title="All items from this day">14&nbsp;Aug&nbsp;2015</a></time>'
        )

    def test_returns_time_with_no_link(self):
        "Link isn't added if show='time' even if link_to_day=True."
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), show='time', link_to_day=True),
            '<time datetime="2015-08-14 13:34:56">13:34</time>'
        )


    def test_smartypants(self):
        self.assertEqual(
            smartypants("""This... isn't -- "special"."""),
            "This&#8230; isn&#8217;t &#8212; &#8220;special&#8221;."
        )
