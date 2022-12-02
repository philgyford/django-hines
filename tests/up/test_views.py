from django.test import TestCase


class ViewTests(TestCase):
    def test_up(self):
        """Up should respond with a success 200."""
        response = self.client.get("/up/", follow=True)
        self.assertEqual(response.status_code, 200)
