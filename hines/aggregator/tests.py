from django.test.client import Client
from django.test import TestCase

class ViewsTestCase(TestCase):
    
    fixtures = ['test_data.json', ]

    def test_homepage(self):
        '''Test if the homepage renders.'''
        c = Client()
        response = c.get('/')
        self.failUnlessEqual(response.status_code, 200)

    def test_feed(self):
        '''Test if the RSS feed renders.'''
        c = Client()
        response = c.get('/feed/')
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

