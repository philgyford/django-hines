from django.test import TestCase
from django.test.client import Client
from people.models import Person


class PeopleBaseTestCase(TestCase):
    fixtures = [
                '../fixtures/test_data.json',
                '../../books/fixtures/test_data.json',
                '../../aggregator/fixtures/test_data.json',
                ]

class ViewsTestCase(PeopleBaseTestCase):

    def test_person_detail(self):
        c = Client()
        response = c.get('/person/5/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context['person'].name, 'William Gibson')
        self.failUnlessEqual(len(response.context['publication_list']), 3)
        self.failUnlessEqual(len(response.context['reading_years']), 2)

    def test_person_name(self):
        p = Person(title='Sir', first_name='Bill', middle_name='Q.', last_name='Bloggs', suffix='Jr.')
        p.save()
        self.failUnlessEqual(p.name, 'Sir Bill Q. Bloggs Jr.')


