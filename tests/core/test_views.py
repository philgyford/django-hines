from django.http.response import Http404
from django.test import RequestFactory, TestCase

from hines.core import views


class ViewTestCase(TestCase):
    """
    Parent class to use with all the other view test cases.
    """

    def setUp(self):
        self.factory = RequestFactory()
        # We use '/fake-path/' for all tests because not testing URLs here,
        # and the views don't care what the URL is.
        self.request = self.factory.get('/fake-path/')


class HomeViewTestCase(ViewTestCase):

    def test_response_200(self):
        "It should respond with 200."
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = views.HomeView.as_view()(self.request)
        self.assertEqual(response.template_name[0], 'core/home.html')

