from django.test import TestCase
from django.urls import resolve, reverse

from hines.core import views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class CoreUrlsTestCase(TestCase):

    def test_home_url(self):
        self.assertEqual(reverse('hines:home'), '/terry/')

    def test_home_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/terry/').func.__name__,
                         views.HomeView.__name__)

    def test_day_archive_url(self):
        self.assertEqual(
            reverse('hines:day_archive',
                        kwargs={'year': 2017, 'month': '04', 'day': '03',}
                    ),
            '/terry/2017/04/03/'
        )

    def test_day_archive_view(self):
        self.assertEqual(resolve('/terry/2017/04/03/').func.__name__,
                        views.DayArchiveView.__name__)

