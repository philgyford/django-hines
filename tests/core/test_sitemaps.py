from django.test import Client, TestCase


class SitemapTestCase(TestCase):
    "Only testing that the sitemaps exist and return 200"

    def test_sitemap(self):
        response = Client().get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
