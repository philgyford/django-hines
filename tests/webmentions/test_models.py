from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings

from hines.webmentions.models.models import OutgoingWebmention

from tests import ModelMixinTestCase, override_app_settings
from hines.webmentions.factories import (
    IncomingWebmentionFactory,
    OutgoingWebmentionFactory,
)
from hines.webmentions.models import MentionableMixin


class MentionableMixinTestCase(ModelMixinTestCase):
    """
    Testing the raw mixin class, without mocked methods.
    """

    mixin = MentionableMixin

    def test_get_all_html(self):
        "It should raise an ImproperlyConfigured error"
        obj = self.model()
        with self.assertRaises(ImproperlyConfigured):
            obj.get_all_html()

    def test_get_absolute_url_with_domain(self):
        "It should raise an ImproperlyConfigured error"
        obj = self.model()
        with self.assertRaises(ImproperlyConfigured):
            obj.get_absolute_url_with_domain()


class MockedMentionableMixinTestCase(ModelMixinTestCase):
    """
    Adding mocked methods that would otherwise raise exceptions.

    We add get_all_html() and get_absolute_url_with_domain() methods
    to self.mixin so that they don't raise exceptions when testing
    other things.
    """

    mixin = MentionableMixin

    # Prevent a clash with the model name used in the previous TestCase:
    class_name = "MockedMentionableMixin"

    @classmethod
    def setUpClass(cls):
        """
        Add required methods to our mixin to prevent ImproperlyConfigured
        exceptions
        """
        super().setUpClass()

        def get_all_html(self):
            return "<p>Hello</p>"

        def get_absolute_url_with_domain(self):
            return "https://example.org/foo"

        cls.mixin.get_all_html = get_all_html
        cls.mixin.get_absolute_url_with_domain = get_absolute_url_with_domain

    def setUp(self):
        super().setUp()
        self.obj = self.model.objects.create()

    def tearDown(self):
        super().tearDown()

        # Without the following line I was getting errors like this:
        #
        # django.db.utils.IntegrityError: insert or update on table
        # "webmentions_outgoingwebmention" violates foreign key
        # constraint
        # "webmentions_outgoing_content_type_id_ec447b74_fk_django_co"
        # DETAIL:  Key (content_type_id)=(51) is not present in table
        # "django_content_type".
        ContentType.objects.clear_cache()

    def test_incoming_webmentions(self):
        "Method should return a queryset of public, validated incoming webmentions"

        wm1 = IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=True
        )
        wm2 = IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=True
        )
        # Non-public:
        IncomingWebmentionFactory(
            content_object=self.obj, is_public=False, is_validated=True
        )
        # Not validated:
        IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=False
        )
        # On a different object:
        IncomingWebmentionFactory(
            content_object=self.model.objects.create(),
            is_public=True,
            is_validated=True,
        )

        mentions = self.obj.incoming_webmentions

        self.assertEqual(len(mentions), 2)
        self.assertIn(wm1, mentions)
        self.assertIn(wm2, mentions)

    def test_outgoing_webmentions(self):
        "Method should return a queryset of outgoing webmentions"

        wm1 = OutgoingWebmentionFactory(content_object=self.obj)
        wm2 = OutgoingWebmentionFactory(content_object=self.obj)
        # # On a different object:
        OutgoingWebmentionFactory(content_object=self.model.objects.create())

        mentions = self.obj.outgoing_webmentions

        self.assertEqual(len(mentions), 2)
        self.assertIn(wm1, mentions)
        self.assertIn(wm2, mentions)

    # incoming_webmentions_allowed

    @override_app_settings(INCOMING_WEBMENTIONS_ALLOWED=False)
    def test_incoming_webmentions_allowed_global_setting_false(self):
        "If global setting is False, should return false"
        self.obj.allow_incoming_webmentions = True
        self.assertFalse(self.obj.incoming_webmentions_allowed)

    @override_app_settings(INCOMING_WEBMENTIONS_ALLOWED=True)
    def test_incoming_webmentions_allowed_post_false(self):
        "If Post setting is False, should return false"
        self.obj.allow_incoming_webmentions = False
        self.assertFalse(self.obj.incoming_webmentions_allowed)

    @override_app_settings(INCOMING_WEBMENTIONS_ALLOWED=True)
    def test_incoming_webmentions_allowed_true(self):
        "If all are True, it should return True"
        self.obj.allow_incoming_webmentions = True
        self.assertTrue(self.obj.incoming_webmentions_allowed)

    # outgoing_webmentions_allowed

    @override_app_settings(OUTGOING_WEBMENTIONS_ALLOWED=False)
    def test_outgoing_webmentions_allowed_global_setting_false(self):
        "If global setting is False, should return false"
        self.obj.allow_outgoing_webmentions = True
        self.assertFalse(self.obj.outgoing_webmentions_allowed)

    @override_app_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    def test_outgoing_webmentions_allowed_post_false(self):
        "If Post setting is False, should return false"
        self.obj.allow_outgoing_webmentions = False
        self.assertFalse(self.obj.outgoing_webmentions_allowed)

    @override_app_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    def test_outgoing_webmentions_allowed_true(self):
        "If all are True, it should return True"
        self.obj.allow_outgoing_webmentions = True
        self.assertTrue(self.obj.outgoing_webmentions_allowed)

    # post_save signal

    def test_post_save_signal_public_validated(self):
        "When saving a public, validated IncomingWebmention, count should be set"
        self.assertEqual(self.obj.incoming_webmention_count, 0)
        IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=True
        )
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.incoming_webmention_count, 1)

    def test_post_save_signal_hidden(self):
        "When saving a non-public IncomingWebmention, count should be set"
        self.assertEqual(self.obj.incoming_webmention_count, 0)
        IncomingWebmentionFactory(
            content_object=self.obj, is_public=False, is_validated=True
        )
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.incoming_webmention_count, 0)

    def test_post_save_signal_unvalidated(self):
        "When saving an unvalidated IncomingWebmention, count should be set"
        self.assertEqual(self.obj.incoming_webmention_count, 0)
        IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=False
        )
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.incoming_webmention_count, 0)

    # post_delete signal

    def test_post_delete_signal(self):
        "When deleting an IncomingWebmention, count should be set"
        wm = IncomingWebmentionFactory(
            content_object=self.obj, is_public=True, is_validated=True
        )
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.incoming_webmention_count, 1)
        wm.delete()
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.incoming_webmention_count, 0)

    # generate_outgoing_webmentions

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    def test_generates_outgoing(self, get_all_html):
        "It should generate outgoing webmentions on save"
        get_all_html.return_value = (
            '<a href="https://bibble.org/foo">Foo</a>'
            '<a href="http://bobble.com/bar">bar</a>'
        )

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 2)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    def test_generate_outgoing_ignores_links_to_self_without_domain(self, get_all_html):
        "It should ignore any links that don't have http: etc"
        get_all_html.return_value = '<a href="/foo">Foo</a><a href="bar">bar</a>'

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 0)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    def test_generate_outgoing_ignores_links_to_self_with_domain(self, get_all_html):
        "It should ignore any links that are to the current site"
        get_all_html.return_value = (
            '<a href="http://example.com/foo">Foo</a>'
            '<a href="https://example.com/bar">bar</a>'
        )

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 0)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    def test_generate_outgoing_does_not_generate_duplicates_from_html(
        self, get_all_html
    ):
        "It should not include duplicate links in the html"
        get_all_html.return_value = (
            '<a href="https://bibble.org/foo">Foo</a>'
            '<a href="https://bibble.org/foo">Foo2</a>'
        )

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 1)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    @patch("hines.webmentions.models.MentionableMixin.get_absolute_url_with_domain")
    def test_generate_outgoing_does_not_generate_duplicates_in_db(
        self, get_abs_url, get_all_html
    ):
        "It should not create a mention if it already exists in DB"
        get_abs_url.return_value = "http://example.com/posts/my-post/"
        get_all_html.return_value = '<a href="https://bibble.org/foo">Foo</a>'

        OutgoingWebmention.objects.create(
            source_url="http://example.com/posts/my-post/",
            target_url="https://bibble.org/foo",
            content_type=ContentType.objects.get_for_model(self.model),
            object_pk=self.obj.pk,
        )
        self.assertEqual(len(self.obj.outgoing_webmentions), 1)

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 1)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    @patch("hines.webmentions.models.MentionableMixin.get_absolute_url_with_domain")
    def test_generate_outgoing_deletes_removed_links(self, get_abs_url, get_all_html):
        """
        It should remove any unsent webmentions if deleted from HTML
        i.e. if there's a WAITING outgoing webmention in the DB, but we
        save the object and now that link isn't in its HTML, we should
        remove the webmention from the DB.
        """
        get_abs_url.return_value = "http://example.com/posts/my-post/"
        get_all_html.return_value = ""

        OutgoingWebmention.objects.create(
            source_url="http://example.com/posts/my-post/",
            target_url="https://bibble.org/foo",
            content_type=ContentType.objects.get_for_model(self.model),
            object_pk=self.obj.pk,
            status=OutgoingWebmention.Status.WAITING,
        )
        self.assertEqual(len(self.obj.outgoing_webmentions), 1)

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 0)

    @override_settings(OUTGOING_WEBMENTIONS_ALLOWED=True)
    @patch("hines.webmentions.models.MentionableMixin.get_all_html")
    @patch("hines.webmentions.models.MentionableMixin.get_absolute_url_with_domain")
    def test_generate_outgoing_keeps_sent_links(self, get_abs_url, get_all_html):
        """
        It should not remove any already sent webmentions
        even if they're no longer in the HTML.
        """
        get_abs_url.return_value = "http://example.com/posts/my-post/"
        get_all_html.return_value = ""

        OutgoingWebmention.objects.create(
            source_url="http://example.com/posts/my-post/",
            target_url="https://bibble.org/foo",
            content_type=ContentType.objects.get_for_model(self.model),
            object_pk=self.obj.pk,
            status=OutgoingWebmention.Status.OK,
        )
        self.assertEqual(len(self.obj.outgoing_webmentions), 1)

        self.obj.save()

        self.assertEqual(len(self.obj.outgoing_webmentions), 1)
