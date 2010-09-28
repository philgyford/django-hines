from django.test.client import Client
from django.test import TestCase

class WeblogClientTests(TestCase):
    
    fixtures = ['../../aggregator/fixtures/test_data.json', ]

    def setUp(self):
        pass

    def tearDown(self):
        pass


# Testing Views/URLs.

    def test_WritingBlogIndex(self):
        '''Test if the Writing blog homepage renders.'''
        c = Client()
        response = c.get('/writing/')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_LinksBlogIndex(self):
        '''Test if the Links blog homepage renders.'''
        c = Client()
        response = c.get('/links/')
        self.failUnlessEqual(response.status_code, 200)

    def test_CommentsBlogIndex(self):
        '''Test if the Comments blog homepage renders.'''
        c = Client()
        response = c.get('/comments/')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_WeblogArchiveMonth(self):
        '''Test if an archive page for a month within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/09/')
        self.failUnlessEqual(response.status_code, 200)

    def test_WeblogEntryDetail(self):
        '''Test if a page for a single Entry within a weblog renders.'''
        c = Client()
        response = c.get('/writing/2010/09/27/featured-writing-post/')
        self.failUnlessEqual(response.status_code, 200)

    def test_WeblogEntryDraft404(self):
        '''Test if a page for a single DRAFT Entry within a weblog 404s.'''
        c = Client()
        response = c.get('/writing/2010/09/27/draft-post/')
        self.failUnlessEqual(response.status_code, 404)
        
    def test_WeblogTag(self):
        '''Test if a page for a tag within a weblog renders.'''
        c = Client()
        response = c.get('/writing/animals/')
        self.failUnlessEqual(response.status_code, 200)

    def test_WeblogTag404(self):
        '''Test if a page for a non-existent tag within a weblog 404s.'''
        c = Client()
        response = c.get('/writing/fish/')
        self.failUnlessEqual(response.status_code, 404)

    def test_WeblogFeed(self):
        '''Test if the RSS feed renders.'''
        c = Client()
        response = c.get('/writing/feed/')
        self.failUnlessEqual(response.status_code, 200)