from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from tests import ModelMixinTestCase, override_app_settings
from hines.webmentions.factories import (
    IncomingWebmentionFactory,
    OutgoingWebmentionFactory,
)
from hines.webmentions.models import MentionableMixin


class MentionableMixinTestCase(ModelMixinTestCase):
    mixin = MentionableMixin

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

    def test_get_all_html(self):
        "It should raise an ImproperlyConfigured error"
        with self.assertRaises(ImproperlyConfigured):
            self.obj.get_all_html()

    def test_get_absolute_url_with_domain(self):
        "It should raise an ImproperlyConfigured error"
        with self.assertRaises(ImproperlyConfigured):
            self.obj.get_absolute_url_with_domain()

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
