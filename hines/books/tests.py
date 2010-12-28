import datetime
from aggregator.models import Aggregator
from django.test import TestCase
from django.test.client import Client
from books.models import Publication

class BooksBaseTestCase(TestCase):
    fixtures = [
                '../fixtures/test_data.json',
                '../../people/fixtures/test_data.json',
                '../../aggregator/fixtures/test_data.json',
                ]

class ViewsTestCase(BooksBaseTestCase):

    def test_books_index(self):
        '''Test if the Books homepage renders.'''
        c = Client()
        response = c.get('/reading/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['publications_inprogress']), 1)
        self.failUnlessEqual(response.context['publications_inprogress'][0].name, 'Vol. 32 No. 17, 9 September 2010')
        self.failUnlessEqual(len(response.context['publications_unread']), 1)
        self.failUnlessEqual(response.context['publications_unread'][0].name, 'Idoru')
        self.failUnlessEqual(response.context['publications_unread'][0].authors_names, 'William Gibson')
        self.failUnlessEqual(len(response.context['reading_years']), 2)

    def test_reading_archive_year(self):
        '''Test if the reading archive page renders.'''
        c = Client()
        response = c.get('/reading/2010/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context['publication_list']), 3)
        self.failUnlessEqual(response.context['publication_list'][1].name, 'The Difference Engine')
        self.failUnlessEqual(response.context['year'], '2010')
        self.failUnlessEqual(len(response.context['reading_years']), 2)

    def test_publication(self):
        '''Test if the page for a single publication displays.'''
        c = Client()
        response = c.get('/reading/publication/7/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['publication'].name, 'The Difference Engine')
        self.failUnlessEqual(len(response.context['reading_years']), 2)

    def test_publication_series(self):
        '''Test if the page for a single publication in a series displays.'''
        c = Client()
        response = c.get('/reading/publication/8/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['publication'].name, 'Vol. 32 No. 18, 23 September 2010')
        self.failUnlessEqual(len(response.context['series_publications']), 1)


class PublicationTestCase(BooksBaseTestCase):

    def test_publication_series(self):
        lrb = Publication.objects.get(pk=8)
        self.failUnlessEqual(lrb.__unicode__(), 'London Review of Books: Vol. 32 No. 18, 23 September 2010')
        book = Publication.objects.get(pk=7)
        self.failUnlessEqual(book.__unicode__(), 'The Difference Engine')

    def test_publication_authors(self):
        book = Publication.objects.get(pk=7)
        self.failUnlessEqual(book.authors_names, 'William Gibson and Bruce Sterling (Test Role)')
        self.failUnlessEqual(book.authors_names_linked, '<a href="/person/5/">William Gibson</a> and <a href="/person/6/">Bruce Sterling</a> (Test Role)')

    def test_publication_readings(self):
        book = Publication.objects.get(pk=7)
        self.failUnlessEqual(book.readings[0].start_date, datetime.date(year=2010,month=9,day=1))
        self.failUnlessEqual(book.readings[0].end_date, datetime.date(year=2010,month=9,day=15))

    def test_publication_amazon(self):
        book = Publication.objects.get(pk=7)
        current_aggregator = Aggregator.objects.get_current()

        amazon_url_us = 'http://www.amazon.com/gp/product/055329461X/' 
        if current_aggregator.amazon_id_us:
            amazon_url_us += '?tag='+current_aggregator.amazon_id_us
        self.failUnlessEqual(book.amazon_url_us, amazon_url_us)

        amazon_url_gb = 'http://www.amazon.co.uk/gp/product/0575600292/' 
        if current_aggregator.amazon_id_gb:
            amazon_url_gb += '?tag='+current_aggregator.amazon_id_gb
        self.failUnlessEqual(book.amazon_url_gb, amazon_url_gb)

    def test_publication_readings(self):
        book = Publication.objects.get(pk=7)
        self.failUnlessEqual(len(book.readings), 1)
        self.failUnlessEqual(book.readings[0].read_but_unfinished, True)
        
        book = Publication.objects.get(pk=6)
        self.failUnlessEqual(len(book.readings), 2)
        self.failUnlessEqual(book.readings[0].finished, True)

        book = Publication.objects.get(pk=9)
        self.failUnlessEqual(len(book.readings), 0)

    def test_publication_day(self):
        publications_day = Publication.objects.read_on_day(datetime.date(year=2010,month=9,day=15))
        self.failUnlessEqual(len(publications_day), 2)
        self.failUnlessEqual(publications_day[0].name, 'The Difference Engine')
        self.failUnlessEqual(publications_day[1].name, 'Vol. 32 No. 18, 23 September 2010')



