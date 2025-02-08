from ditto.pinboard.factories import BookmarkFactory
from django.test import TestCase

from hines.users.models import User


class BookmarkTagAutocompleteTestCase(TestCase):
    "Testing while logged out"

    def test_response(self):
        "It should redirect to login page"
        response = self.client.get("/terry/links/bookmark-tag-autocomplete/?q=foo")
        self.assertRedirects(
            response,
            "/backstage/login/?next=/terry/links/bookmark-tag-autocomplete/?q=foo",
            status_code=302,
            target_status_code=200,
        )


class AuthenticatedBookmarkTagAutocompleteTestCase(TestCase):
    "Testing while logged in"

    def setUp(self):
        super().setUp()
        user = User.objects.create_user("bob", "bob@example.com", "pass")
        self.client.force_login(user=user)

    def test_response_authenticated(self):
        "It should respond with 200 for authenticated users"
        response = self.client.get("/terry/links/bookmark-tag-autocomplete/?q=foo")
        self.assertEqual(response.status_code, 200)

    def test_tags(self):
        "It should return the requested tags, most popular first"
        link_1 = BookmarkFactory()
        link_1.tags.set(["foo"])
        tag_1 = link_1.tags.first()

        link_2 = BookmarkFactory()
        link_2.tags.set(["food"])
        tag_2 = link_2.tags.first()

        link_3 = BookmarkFactory()
        link_3.tags.set(["bar"])

        link_4 = BookmarkFactory()
        link_4.tags.set(["food"])

        response = self.client.get("/terry/links/bookmark-tag-autocomplete/?q=foo")
        self.assertJSONEqual(
            response.content,
            {
                "results": [
                    {"id": f"{tag_2.id}", "text": "food", "selected_text": "food"},
                    {"id": f"{tag_1.id}", "text": "foo", "selected_text": "foo"},
                ],
                "pagination": {"more": False},
            },
        )
