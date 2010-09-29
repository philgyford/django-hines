from django.test.client import Client
from django.test import TestCase
from aggregator.models import Aggregator


class AggregatorBaseTestCase(TestCase):
    
    fixtures = ['test_data.json', ]


class ViewsTestCase(AggregatorBaseTestCase):

    def test_homepage(self):
        '''Test if the homepage renders.'''
        c = Client()
        response = c.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_aggregator_day(self):
        '''Test if a page for an aggregated day renders.'''
        c = Client()
        response = c.get('/2010/09/26/')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_about(self):
        'Test if the about page renders.'
        c = Client()
        response = c.get('/about/')
        self.failUnlessEqual(response.status_code, 200)


class AggregatorTestCase(AggregatorBaseTestCase):
    
    def test_feed_local(self):
        '''Test if the local RSS feed renders.'''
        current_aggregator = Aggregator.objects.get_current()
        c = Client()
        response = c.get(current_aggregator.get_entries_feed_url())
        self.failUnlessEqual(response.status_code, 200)
        
    def test_feed_remote(self):
        '''Test if the remote RSS feed is used if it's set'.'''
        current_aggregator = Aggregator.objects.get_current()
        current_aggregator.remote_entries_feed_url = 'http://feeds.feedburner.com/PhilGyford'
        current_aggregator.save()
        self.failUnlessEqual( current_aggregator.get_entries_feed_url(), 'http://feeds.feedburner.com/PhilGyford')
        
        current_aggregator.remote_entries_feed_url = ''
        current_aggregator.save()