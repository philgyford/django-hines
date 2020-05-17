from django.test import TestCase

from hines.users.factories import UserFactory


class UserTestCase(TestCase):
    def test_display_name_first_and_last(self):
        user = UserFactory(first_name="Bob", last_name="Ferris")
        self.assertEqual(user.display_name, "Bob Ferris")

    def test_display_name_first_only(self):
        user = UserFactory(first_name="Bob", last_name="")
        self.assertEqual(user.display_name, "Bob")

    def test_display_name_last_only(self):
        user = UserFactory(first_name="", last_name="Ferris")
        self.assertEqual(user.display_name, "Ferris")

    def test_display_name_no_name(self):
        user = UserFactory(first_name="", last_name="", username="bob")
        self.assertEqual(user.display_name, "bob")
