from django.db import connection
from django.db.models.base import ModelBase
from django.test import TestCase
import responses

from hines.core import app_settings


def override_app_settings(**test_settings):
    """
    A decorator for overriding settings that takes uses our core.app_settings
    module.

    Because if we use the standard @override_settings decorator that doesn't
    work with our app_settings, which are set before we override them.

    Use like:

        from django.test import TestCase
        from tests.core import override_app_settings

        class MyTestCase(TestCase):

            @override_app_settings(MY_SETTING='hello')
            def test_does_a_thing(self):
                # ...

    Doesn't seem to work if applied to a TestCase class, only the
    individual test methods. Or maybe that's only if you try to
    override two settings on a class.

    From https://gist.github.com/integricho/6502772fd3c144c719a7
    """

    def _override_app_settings(func):
        def __override_app_settings(*args, **kwargs):
            old_values = dict()
            for key, value in test_settings.items():
                old_values[key] = getattr(app_settings, key)
                setattr(app_settings, key, value)

            result = func(*args, **kwargs)

            for key, value in test_settings.items():
                setattr(app_settings, key, old_values[key])

            return result

        return __override_app_settings

    return _override_app_settings


class ModelMixinTestCase(TestCase):
    """
    Test Case for abstract mixin models.

    Subclass and set cls.mixin to your desired mixin.
    access your model using cls.model.

    From https://stackoverflow.com/a/57586891/250962
    """

    mixin = None
    model = None

    # If you use the same mixin for more than one TestCase object,
    # you'll get errors about the Model "was already registered".
    # This is because the models created for each TestCase will have
    # the same name, of "__Test" + cls.mixin.__name__
    # To avoid this, set a new name for the class using this property
    # in your TestCase.
    class_name = None

    @classmethod
    def setUpClass(cls) -> None:
        # Create a real model from the mixin
        class_name = cls.class_name if cls.class_name else f"__Test{cls.mixin.__name__}"
        cls.model = ModelBase(
            class_name,
            (cls.mixin,),
            {"__module__": cls.mixin.__module__},
        )

        # Use schema_editor to create schema
        with connection.schema_editor() as editor:
            editor.create_model(cls.model)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        # allow the transaction to exit
        super().tearDownClass()

        # Use schema_editor to delete schema
        with connection.schema_editor() as editor:
            editor.delete_model(cls.model)

        # close the connection
        connection.close()


class ResponsesMixin(object):
    """
    Add this to a TestCase class to activate responses,
    instead of using the `@responses.activate` decorator on every
    test method.
    https://gist.github.com/asfaltboy/bebd2c6943c34b0b27a7e3060448049b
    """

    def setUp(self):
        assert responses, "responses package required to use ResponsesMixin"
        responses.start()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        responses.stop()
        responses.reset()
