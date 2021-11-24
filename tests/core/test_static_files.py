from django.test import TestCase

from bs4 import BeautifulSoup


class StaticFilesTestCase(TestCase):
    def test_css_file_exists(self):
        "There should be one CSS file linked to and it should exist."
        response = self.client.get("/")

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.findAll("link", {"rel": "stylesheet"})
        self.assertEqual(len(links), 1)

        response = self.client.get(links[0]["href"])
        self.assertEqual(response.status_code, 200)

    def test_js_file_exists(self):
        "There should be one JS file linked to and it should exist."
        response = self.client.get("/")

        soup = BeautifulSoup(response.content, "html.parser")
        scripts = soup.findAll("script", {"src": True})
        self.assertEqual(len(scripts), 1)

        response = self.client.get(scripts[0]["src"])
        self.assertEqual(response.status_code, 200)
