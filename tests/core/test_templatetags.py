from unittest.mock import patch

from django.test import TestCase

from hines.core.templatetags.hines_core import display_time
from . import make_datetime


class DisplayTimeTestCase(TestCase):

    def test_returns_time_with_no_link(self):
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56')),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14&nbsp;Aug&nbsp;2015</time>'
        )

    @patch('hines.core.templatetags.hines_core.reverse')
    def test_returns_time_with_link(self, reverse):
        reverse.return_value = '/2015/08/14/'
        self.assertEqual(
            display_time(make_datetime('2015-08-14 13:34:56'), True),
            '<time datetime="2015-08-14 13:34:56">13:34 on <a href="/2015/08/14/" title="All items from this day">14&nbsp;Aug&nbsp;2015</a></time>'
        )

