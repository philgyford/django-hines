from django.test.client import Client
from django.test import TestCase

class AggregatorClientTests(TestCase):
    
    fixtures = ['test_data.json', ]

    def setUp(self):
        pass

    def tearDown(self):
        pass


# Testing Views/URLs.

    def test_HomePage(self):
        '''Test if the homepage renders.'''
        c = Client()
        response = c.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_Feed(self):
        '''Test if the RSS feed renders.'''
        c = Client()
        response = c.get('/feed/')
        self.failUnlessEqual(response.status_code, 200)
        
# Test Flatpages
    def test_About(self):
        'Test if the about page renders.'
        c = Client()
        response = c.get('/about/')
        self.failUnlessEqual(response.status_code, 200)

# Aggregator tests. Should be elsewhere really...
    def test_AggregatorDay(self):
        '''Test if a page for an aggregated day renders.'''
        c = Client()
        response = c.get('/2010/09/26/')
        self.failUnlessEqual(response.status_code, 200)
