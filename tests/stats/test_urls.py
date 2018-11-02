from django.test import TestCase
from django.urls import resolve, reverse

from hines.stats import views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class StatsUrlsTestCase(TestCase):

    def test_home_url(self):
        self.assertEqual(reverse('stats:home'), '/terry/stats/')

    def test_home_view(self):
        "Should use the correct view."
        self.assertEqual(resolve('/terry/stats/').func.__name__,
                         views.StatsView.__name__)


    def test_creating_redirect(self):
        response = self.client.get('/terry/stats/creating/', follow=True)
        self.assertEqual(response.redirect_chain, [('/terry/stats/', 302)])


    def test_stats_detail_url(self):
        self.assertEqual(
            reverse('stats:stats_detail', kwargs={'slug': 'consuming'}),
            '/terry/stats/consuming/')

    def test_stats_detail_view(self):
        self.assertEqual(resolve('/terry/stats/consuming/').func.__name__,
                        views.StatsView.__name__)
