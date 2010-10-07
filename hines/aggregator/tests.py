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
        self.failUnlessEqual(len(response.context['blogs']), 3)
        self.failUnlessEqual(response.context['blogs'][0].slug, 'writing')
        self.failUnlessEqual(len(response.context['blogs'][0].entries), 2)
        self.failUnlessEqual(response.context['blogs'][1].slug, 'links')
        self.failUnlessEqual(len(response.context['blogs'][1].entries), 1)
        self.failUnlessEqual(response.context['blogs'][2].slug, 'comments')
        self.failUnlessEqual(len(response.context['blogs'][2].entries), 1)

    def test_aggregator_day(self):
        '''Test if a page for an aggregated day renders.'''
        c = Client()
        response = c.get('/2010/09/26/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['blogs']), 3)
        self.failUnlessEqual(response.context['blogs'][0].slug, 'writing')
        self.failUnlessEqual(len(response.context['blogs'][0].entries), 1)
        self.failUnlessEqual(response.context['blogs'][1].slug, 'links')
        self.failUnlessEqual(len(response.context['blogs'][1].entries), 0)
        self.failUnlessEqual(response.context['blogs'][2].slug, 'comments')
        self.failUnlessEqual(len(response.context['blogs'][2].entries), 0)
        self.failUnlessEqual(response.context['date'].year, 2010)
        self.failUnlessEqual(response.context['date'].month, 9)
        self.failUnlessEqual(response.context['date'].day, 26)
        
    def test_about(self):
        'Test if the about page renders.'
        c = Client()
        response = c.get('/about/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['flatpage'].title, 'About me')

class AggregatorTestCase(AggregatorBaseTestCase):
    
    def test_entries_feed_local(self):
        '''Test if the local Entries RSS feed renders.'''
        current_aggregator = Aggregator.objects.get_current()
        c = Client()
        response = c.get(current_aggregator.get_entries_feed_url())
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, "<title>A featured writing post</title>")
        self.assertContains(response, "writing/2010/09/27/featured-writing-post/</link>")
        self.assertContains(response, "writing/2010/09/27/featured-writing-post/</guid>")
        self.assertContains(response, "<content:encoded>&lt;p&gt;Sed metus leo, tristique", msg_prefix="content:encoded element missing from feed.")
        self.assertContains(response, "<title>A published Writing post</title>", msg_prefix="A Writing entry missing from feed.")
        self.assertContains(response, "<title>The Online Photographer: 'A Leica for a Year' a Year Later</title>", msg_prefix="A Writing entry missing from feed.")
        self.assertContains(response, "<title>A links post from August</title>", msg_prefix="No :inks entry in feed.")
        
    def test_entries_feed_remote(self):
        '''Test if the remote Entries RSS feed is used if it's set'.'''
        current_aggregator = Aggregator.objects.get_current()
        current_aggregator.remote_entries_feed_url = 'http://feeds.feedburner.com/PhilGyford'
        current_aggregator.save()
        self.failUnlessEqual( current_aggregator.get_entries_feed_url(), 'http://feeds.feedburner.com/PhilGyford')
        current_aggregator.remote_entries_feed_url = ''
        current_aggregator.save()
        
    def test_comments_feed_local(self):
        '''Test if the local Comments RSS feed renders.'''
        current_aggregator = Aggregator.objects.get_current()
        c = Client()
        response = c.get(current_aggregator.get_comments_feed_url())
        self.failUnlessEqual(response.status_code, 200)

    def test_comments_feed_remote(self):
        '''Test if the remote Comments RSS feed is used if it's set'.'''
        current_aggregator = Aggregator.objects.get_current()
        current_aggregator.remote_comments_feed_url = 'http://feeds.feedburner.com/PhilGyfordComments'
        current_aggregator.save()
        self.failUnlessEqual( current_aggregator.get_comments_feed_url(), 'http://feeds.feedburner.com/PhilGyfordComments')
        current_aggregator.remote_comments_feed_url = ''
        current_aggregator.save()