from django.test import TestCase
from django.urls import resolve, reverse

from hines.core import views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class CoreUrlsTestCase(TestCase):

    def test_home_url(self):
        self.assertEqual(reverse('hines:home'), '/phil/')

    def test_home_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/phil/').func.__name__,
                         views.HomeView.__name__)

