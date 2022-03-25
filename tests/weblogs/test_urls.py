from django.test import TestCase
from django.urls import resolve, reverse

from hines.weblogs import feeds, views


# Testing that the named URLs map the correct name to URL,
# and that the correct views are called.


class WeblogsUrlsTestCase(TestCase):
    def test_blog_detail_url(self):
        self.assertEqual(
            reverse("weblogs:blog_detail", kwargs={"blog_slug": "my-blog"}),
            "/terry/my-blog/",
        )

    def test_blog_detail_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/").func.view_class, views.BlogDetailView
        )

    def test_blog_archive_url(self):
        self.assertEqual(
            reverse("weblogs:blog_archive", kwargs={"blog_slug": "my-blog"}),
            "/terry/my-blog/archive/",
        )

    def test_blog_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/archive/").func.view_class,
            views.BlogArchiveView,
        )

    def test_blog_feed_rss_url(self):
        self.assertEqual(
            reverse("weblogs:blog_feed_posts_rss", kwargs={"blog_slug": "my-blog"}),
            "/terry/my-blog/feeds/posts/rss/",
        )

    def test_blog_feed_rss_view(self):
        "Should use the correct feed object."
        self.assertIsInstance(
            resolve("/terry/my-blog/feeds/posts/rss/").func, feeds.BlogPostsFeedRSS
        )

    def test_blog_tag_detail_url(self):
        self.assertEqual(
            reverse(
                "weblogs:blog_tag_detail",
                kwargs={"blog_slug": "my-blog", "tag_slug": "my-tag"},
            ),
            "/terry/my-blog/tags/my-tag/",
        )

    def test_blog_tag_detail_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/tags/my-tag/").func.view_class,
            views.BlogTagDetailView,
        )

    def test_post_detail_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_detail",
                kwargs={
                    "blog_slug": "my-blog",
                    "year": "2017",
                    "month": "02",
                    "day": "20",
                    "post_slug": "my-post",
                },
            ),
            "/terry/my-blog/2017/02/20/my-post/",
        )

    def test_post_detail_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/02/20/my-post/").func.view_class,
            views.PostDetailView,
        )

    def test_post_redirect_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_redirect",
                kwargs={
                    "blog_slug": "my-blog",
                    "year": "2017",
                    "month": "02",
                    "day": "20",
                    "post_slug": "my_old_post",
                },
            ),
            "/terry/my-blog/2017/02/20/my_old_post.php",
        )

    def test_post_redirect_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/02/20/my_old_post.php").func.view_class,
            views.PostRedirectView,
        )

    def test_post_redirect_index_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_redirect_index",
                kwargs={
                    "blog_slug": "my-blog",
                    "year": "2017",
                    "month": "02",
                    "day": "20",
                    "post_slug": "my_old_post",
                },
            ),
            "/terry/my-blog/2017/02/20/my_old_post/index.php",
        )

    def test_post_redirect_index_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/02/20/my_old_post/index.php").func.view_class,
            views.PostRedirectView,
        )

    def test_post_day_archive_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_day_archive",
                kwargs={
                    "blog_slug": "my-blog",
                    "year": "2017",
                    "month": "02",
                    "day": "01",
                },
            ),
            "/terry/my-blog/2017/02/01/",
        )

    def test_post_day_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/02/01/").func.view_class,
            views.PostDayArchiveView,
        )

    def test_post_month_archive_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_month_archive",
                kwargs={"blog_slug": "my-blog", "year": "2017", "month": "02"},
            ),
            "/terry/my-blog/2017/02/",
        )

    def test_post_month_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/02/").func.view_class,
            views.PostMonthArchiveView,
        )

    def test_post_year_archive_url(self):
        self.assertEqual(
            reverse(
                "weblogs:post_year_archive",
                kwargs={"blog_slug": "my-blog", "year": "2017"},
            ),
            "/terry/my-blog/2017/",
        )

    def test_post_year_archive_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/my-blog/2017/").func.view_class,
            views.PostYearArchiveView,
        )

    def test_random_phil_2001_url(self):
        self.assertEqual(reverse("weblogs:random_phil_2001"), "/terry/random-phil/")

    def test_random_phil_2001_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/random-phil/").func.view_class, views.RandomPhilView
        )

    def test_random_phil_2002_url(self):
        self.assertEqual(reverse("weblogs:random_phil_2002"), "/terry/random/")

    def test_random_phil_2002_view(self):
        "Should use the correct view."
        self.assertEqual(
            resolve("/terry/random/").func.view_class, views.RandomPhilView
        )
