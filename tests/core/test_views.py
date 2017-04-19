from django.http.response import Http404
from django.test import RequestFactory, TestCase

from tests.core import make_date, make_datetime
from hines.core import views
from hines.weblogs.factories import BlogFactory, PostFactory
from hines.weblogs.models import Post


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
        self.assertEqual(response.template_name[0], 'hines_core/home.html')


class DayArchiveViewTestCase(ViewTestCase):

    def test_response_200(self):
        "It should respond with 200."
        response = views.DayArchiveView.as_view()(
                            self.request, year='2016', month='08', day='31')
        self.assertEqual(response.status_code, 200)

    def test_response_404(self):
        "It should raise 404 if the date is in the future."
        # Apologies to the developer in September 3000 who'll find this fails.
        with self.assertRaises(Http404):
            views.DayArchiveView.as_view()(
                            self.request, year='3000', month='08', day='31')

    def test_templates(self):
        response = views.DayArchiveView.as_view()(
                            self.request, year='2016', month='08', day='31')
        self.assertEqual(response.template_name[0], 'hines_core/archive_day.html')

    def test_context_data_dates(self):
        "Should include the date and next/prev dates."
        response = views.DayArchiveView.as_view()(
                            self.request, year='2016', month='08', day='31')
        self.assertIn('day', response.context_data)
        self.assertEqual(response.context_data['day'], make_date('2016-08-31'))
        self.assertIn('next_day', response.context_data)
        self.assertEqual(response.context_data['next_day'],
                         make_date('2016-09-01'))
        self.assertIn('previous_day', response.context_data)
        self.assertEqual(response.context_data['previous_day'],
                         make_date('2016-08-30'))

    def test_context_data_blogs(self):
        "Should include public Posts from that day."
        b1 = BlogFactory(sort_order=1)
        # Should be included:
        p1a = PostFactory(blog=b1, status=Post.LIVE_STATUS,
                        time_published=make_datetime('2016-08-31 12:00:00'))
        # Draft; shouldn't be included:
        p1b = PostFactory(blog=b1, status=Post.DRAFT_STATUS,
                          time_published=make_datetime('2016-08-31 12:00:00'))
        # Wrong day; shouldn't be included:
        p1c = PostFactory(blog=b1, status=Post.LIVE_STATUS,
                          time_published=make_datetime('2016-08-30 12:00:00'))
        b2 = BlogFactory(sort_order=2)
        # Should be included:
        p2a = PostFactory(blog=b2, status=Post.LIVE_STATUS,
                          time_published=make_datetime('2016-08-31 12:00:00'))

        response = views.DayArchiveView.as_view()(
                            self.request, year='2016', month='08', day='31')
        context = response.context_data
        self.assertIn('blogs', context)
        self.assertEqual(len(context['blogs']), 2)
        self.assertEqual(context['blogs'][0]['blog'], b1)
        self.assertEqual(context['blogs'][0]['post_list'][0], p1a)
        self.assertEqual(context['blogs'][1]['blog'], b2)
        self.assertEqual(context['blogs'][1]['post_list'][0], p2a)

