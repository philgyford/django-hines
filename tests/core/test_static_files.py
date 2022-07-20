from bs4 import BeautifulSoup
from django.contrib.staticfiles.storage import staticfiles_storage
from django.test import TestCase


class StaticFilesTestCase(TestCase):
    def test_css_file_exists(self):
        "There should be one CSS file linked to and it should exist."
        response = self.client.get("/")

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.findAll("link", {"rel": "stylesheet"})
        self.assertEqual(len(links), 1)

        # Remove "/static/" from the start:
        path = links[0]["href"][8:]
        self.assertTrue(staticfiles_storage.exists(path))

    def test_js_file_exists(self):
        "There should be one JS file linked to and it should exist."
        response = self.client.get("/")

        soup = BeautifulSoup(response.content, "html.parser")
        scripts = soup.findAll("script", {"src": True})
        self.assertEqual(len(scripts), 1)

        # Remove "/static/" from the start:
        path = scripts[0]["src"][8:]
        self.assertTrue(staticfiles_storage.exists(path))
