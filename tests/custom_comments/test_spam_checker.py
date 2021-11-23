from urllib.parse import unquote_plus

from django.conf import settings
from django.contrib.messages import get_messages
from django.test import override_settings, TestCase

import responses

from hines.custom_comments.forms import CustomCommentForm
from hines.custom_comments.models import CustomComment
from hines.weblogs.factories import PostFactory
from hines.users.factories import UserFactory


@override_settings(HINES_AKISMET_API_KEY="abcd1234", HINES_USE_HCAPTCHA=False)
class TestCommentForSpamTestCase(TestCase):
    """
    Testing the spam_checker.test_comment_for_spam() method.

    That method itself doesn't do much but we're testing the full
    process of sending data to Akismet and dealing with the response.

    So we're effectively also testing spam_checker.is_akismet_spam()
    here, with the idea that we could replace it and call
    the replacement from test_comment_for_spam() and these tests
    should still pass.

    We set HINES_USE_HCAPTCHA to False because I'm not sure how to test
    the form with the hCaptcha field in place.
    """

    def add_response(self, body):
        """Mock the response from the Akismet API
        body - text body for the response
        """
        responses.add(
            responses.POST,
            "https://abcd1234.rest.akismet.com/1.1/comment-check",
            body=body,
            status=200,
        )

    def post_comment(self, data=None):
        """Post a comment on the site.
        data is an optional dict of data for the form submission.
        It is passed on to make_comment_form_data() which will add any
        missing required form fields using default values.
        Returns the request object.
        """
        data = self.make_comment_form_data(data=data)
        r = self.client.post("/comments/post/", data, REMOTE_ADDR="1.2.3.4")
        return r

    def make_comment_form_data(self, data=None):
        """Make data for a comment submission.
        data can be a dict of data submitted in the comment form.
        """
        post = PostFactory()
        form = CustomCommentForm(post)

        if data is None:
            data = {
                "name": "Bob",
                "email": "bob@example.org",
                "url": "",
                "comment": "Hello",
            }

        data.update(form.initial)
        return data

    def log_user_in(self, **kwargs):
        """Log the user in to self.client.
        Use before a request to self.client to perform that request logged in.
        Any kwargs passed in are passed to create_user()
        The created user is returned.
        """
        user = UserFactory(**kwargs)
        self.client.force_login(user)
        return user

    def get_request_params(self, request):
        "Returns a dict of data from a request.body string"
        params = dict(i.split("=") for i in request.body.split("&"))
        for k, v in params.items():
            # Not 100% sure unquote_plus() is the correct method for
            # decoding a POST body but it seems to work so far...
            params[k] = unquote_plus(v)
        return params

    @responses.activate
    def test_calls_akimset_api(self):
        "Posting a comment when there's an API key should call Akismet"
        # Add response for a ham comment:
        self.add_response("false")
        self.post_comment()

        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].response.text, "false")

    @responses.activate
    def test_publishes_ham_comment(self):
        "Posting a ham comment should result in it being public"
        # Add response for a ham comment:
        self.add_response("false")
        self.post_comment()

        comment = CustomComment.objects.first()
        self.assertTrue(comment.is_public)

    @responses.activate
    def test_does_not_publish_spam_comment(self):
        "Posting a spam comment should result in it being marked not-public"
        # Add response for a spam comment:
        self.add_response("true")
        self.post_comment()

        comment = CustomComment.objects.first()
        self.assertFalse(comment.is_public)

    @override_settings(MANAGERS=(("Terry", "terry@example.org"),))
    @responses.activate
    def test_spam_comment_generates_message_with_managers(self):
        """Posting a spam comment should result in a message for the user.
        A message that includes a link to email the first of MANAGERS."""
        self.add_response("true")
        response = self.post_comment()

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(len(messages), 1)

        comment = CustomComment.objects.first()
        self.assertEqual(
            str(messages[0]),
            "Your post was flagged as possible spam. If it wasn't then "
            '<a href="mailto:terry@example.org?subject=Flagged comment (ID: '
            f'{comment.id})">email me</a> '
            "to have it published.",
        )

    @responses.activate
    def test_spam_comment_generates_message_with_no_managers(self):
        """Posting a spam comment should result in a message for the user.
        When there are no MANAGERS, it doesn't include a link to email them."""
        del settings.MANAGERS
        self.add_response("true")
        response = self.post_comment()

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your post was flagged as possible spam.")

    @override_settings()
    @responses.activate
    def test_with_no_api_key(self):
        "If no API key is present, Akismet shouldn't be called."
        del settings.HINES_AKISMET_API_KEY
        self.add_response("false")
        self.post_comment()

        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_staff_user_is_not_tested(self):
        "Staff should not have their comments tested by Akismet"
        self.log_user_in(is_staff=True, is_superuser=False)
        self.add_response("false")
        self.post_comment()

        self.assertEqual(len(responses.calls), 0)

    @responses.activate
    def test_not_logged_in_user_is_tested(self):
        "Ordinary users should have their comments tested by Akismet"
        self.add_response("false")
        self.post_comment()

        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_not_logged_in_user_data(self):
        "If the user isn't logged in, their name and email should be sent to Akismet"
        self.add_response("false")
        self.post_comment(
            data={
                "name": "Audrey",
                "email": "audrey@example.org",
                "comment": "Hello",
            }
        )

        params = self.get_request_params(responses.calls[0].request)
        self.assertEqual(params["comment_author"], "Audrey")
        self.assertEqual(params["comment_author_email"], "audrey@example.org")
        self.assertNotIn("comment_author_url", params)

    @responses.activate
    def test_not_logged_in_user_data_with_url(self):
        "If the user isn't logged in, and supplies a URL, it should be sent to Akismet"
        self.add_response("false")
        self.post_comment(
            data={
                "name": "Audrey",
                "email": "audrey@example.org",
                "url": "https://example.org/audrey",
                "comment": "Hello",
            }
        )

        params = self.get_request_params(responses.calls[0].request)
        self.assertEqual(params["comment_author_url"], "https://example.org/audrey")

    @responses.activate
    def test_akismet_error(self):
        "If Akismet returns error, we should display error message and publish comment"
        self.add_response("invalid")
        response = self.post_comment()

        messages = [m.message for m in get_messages(response.wsgi_request)]

        self.assertEqual(len(messages), 1)
        self.assertIn("There was an error when testing the comment", str(messages[0]))
        self.assertIn("invalid", str(messages[0]))

        comment = CustomComment.objects.first()
        self.assertTrue(comment.is_public)
