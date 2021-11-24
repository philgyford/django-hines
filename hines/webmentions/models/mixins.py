from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from hines.core import app_settings


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_incoming_webmentions = models.BooleanField(default=True)
    allow_outgoing_webmentions = models.BooleanField(default=False)

    incoming_webmention_count = models.IntegerField(default=0, blank=False, null=False)

    @property
    def incoming_webmentions(self):
        "A queryset of all the public, validated IncomingWebentions for this object."
        from .models import IncomingWebmention

        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = IncomingWebmention.objects.filter(
            content_type=ctype, object_id=self.id, is_public=True, is_validated=True
        )
        return webmentions

    @property
    def outgoing_webmentions(self):
        "A queryset of all the OutgoingWebentions for this object."
        from .models import OutgoingWebmention

        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = OutgoingWebmention.objects.filter(
            content_type=ctype, object_id=self.id
        )
        return webmentions

    def all_text(self):
        raise ImproperlyConfigured(
            f"{self.__class__} must define an all_text() method because it inherits "
            "from MentionableMixin"
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if (
            self.allow_outgoing_webmentions
            and app_settings.OUTGOING_WEBMENTIONS_ALLOWED
        ):
            self._generate_outgoing_webmentions()

    def _generate_outgoing_webmentions(self):
        # TODO
        pass
