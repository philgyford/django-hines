from django.test import Client, TestCase
from django.urls import resolve, reverse

from hines.core import views

# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class CoreUrlsTestCase(TestCase):
    def test_home_url(self):
        "The very top level page of the site"
        self.assertEqual(reverse("home"), "/")

    def test_home_view(self):
        "Should use the correct view."
        self.assertEqual(resolve("/").func.view_class, views.HomeView)

    def test_hines_home_url(self):
        "The URL at /phil/ or whatever."
        response = Client().get("/terry/", follow=True)
        self.assertEqual(response.redirect_chain, [("/", 302)])

    def test_day_archive_url(self):
        self.assertEqual(
            reverse(
                "hines:day_archive", kwargs={"year": 2017, "month": "04", "day": "03"}
            ),
            "/terry/2017/04/03/",
        )

    def test_day_archive_view(self):
        self.assertEqual(
            resolve("/terry/2017/04/03/").func.view_class, views.DayArchiveView
        )

    def test_reading_home_view(self):
        self.assertEqual(
            resolve("/terry/reading/").func.view_class, views.ReadingHomeView
        )

    def test_author_redirect_view(self):
        self.assertEqual(
            resolve("/terry/reading/author/").func.view_class,
            views.AuthorRedirectView,
        )

    def test_publication_redirect_view(self):
        self.assertEqual(
            resolve("/terry/reading/publication/").func.view_class,
            views.PublicationRedirectView,
        )

    def test_writing_resources_redirect_view(self):
        self.assertEqual(
            resolve(
                "/terry/writing/resources/2017/03/31/folder/test.png"
            ).func.view_class,
            views.WritingResourcesRedirectView,
        )

    def test_archive_redirect_view(self):
        self.assertEqual(
            resolve("/archive/").func.view_class, views.ArchiveRedirectView
        )

    def test_archive_redirect_view_with_path(self):
        self.assertEqual(
            resolve("/archive/my/path/here/").func.view_class,
            views.ArchiveRedirectView,
        )

    def test_tweet_detail_url(self):
        self.assertEqual(
            reverse(
                "twitter:tweet_detail",
                kwargs={"screen_name": "bob", "twitter_id": "1234567890"},
            ),
            "/terry/twitter/bob/1234567890/",
        )

    def test_tweet_detail_view(self):
        self.assertEqual(
            resolve("/terry/twitter/bob/1234567890/").func.view_class,
            views.TweetDetailRedirectView,
        )
