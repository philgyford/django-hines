import logging
from urllib.parse import urldefrag

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from bs4 import BeautifulSoup

from hines.core import app_settings
from hines.core.utils import urls_are_equal
from .models import OutgoingWebmention


log = logging.getLogger(__name__)


class MentionableMixin(models.Model):
    class Meta:
        abstract = True

    allow_incoming_webmentions = models.BooleanField(
        default=True,
        help_text="If true, can still be overridden by the Blog's "
        "equivalent setting, or in Django SETTINGS.",
    )
    allow_outgoing_webmentions = models.BooleanField(
        default=True,
        help_text="If true, can still be overridden by the Blog's "
        "equivalent setting, or in Django SETTINGS.",
    )

    incoming_webmention_count = models.IntegerField(default=0, blank=False, null=False)

    @property
    def incoming_webmentions(self):
        "A queryset of all the public, validated IncomingWebentions for this object."
        from .models import IncomingWebmention

        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = IncomingWebmention.objects.filter(
            content_type=ctype, object_pk=self.pk, is_public=True, is_validated=True
        )
        return webmentions

    @property
    def outgoing_webmentions(self):
        "A queryset of all the OutgoingWebentions for this object."
        from .models import OutgoingWebmention

        ctype = ContentType.objects.get_for_model(self.__class__)
        webmentions = OutgoingWebmention.objects.filter(
            content_type=ctype, object_pk=self.pk
        )
        return webmentions

    @property
    def incoming_webmentions_allowed(self):
        """
        Do we currently accept incoming webmentions on this object?

        A child class might need to alter this depending on other factrors.
        e.g. whether it's an object that's been 'published' yet or not.
        """
        if app_settings.INCOMING_WEBMENTIONS_ALLOWED is not True:
            return False

        elif self.allow_incoming_webmentions is False:
            return False

        else:
            return True

    @property
    def outgoing_webmentions_allowed(self):
        """
        Do we currently allow this object to send webmentions?

        A child class might need to alter this depending on other factrors.
        e.g. whether it's an object that's been 'published' yet or not.
        """
        if app_settings.OUTGOING_WEBMENTIONS_ALLOWED is not True:
            return False

        elif self.allow_outgoing_webmentions is False:
            return False

        else:
            return True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.outgoing_webmentions_allowed:
            self._generate_outgoing_webmentions()

    def get_all_html(self):
        raise ImproperlyConfigured(
            f"{self.__class__} must define an all_html() method because it "
            "inherits from MentionableMixin"
        )

    def get_absolute_url_with_domain(self):
        """
        Should return the FULL URL for this object.
        e.g.
        from hines.core.utils import get_site_url
        return get_site_url() + self.get_absolute_url()
        """
        raise ImproperlyConfigured(
            f"{self.__class__} must define a get_absolute_url_with_domain() method "
            "because it inherits from MentionableMixin"
        )

    def _generate_outgoing_webmentions(self):
        """
        Parses the object's HTML and creates an OutgoingWebmention for
        every outbound link in it. Won't create duplicates.
        """
        target_urls = self._get_outgoing_urls()

        # Delete any existing, WAITING, mentions that are no longer
        # in the HTML.
        for mention in self.outgoing_webmentions:
            if (
                mention.status == OutgoingWebmention.Status.WAITING
                and mention.target_url not in target_urls
            ):
                log.debug(
                    f"Deleting OutgoingWebmention ({mention.pk}) that's no longer "
                    f"present: {mention.target_url}"
                )
                mention.delete()

        # Add any new URLs that are in the HTML
        source_url = self.get_absolute_url_with_domain()
        ctype = ContentType.objects.get_for_model(self.__class__)

        for target_url in target_urls:
            obj, created = OutgoingWebmention.objects.get_or_create(
                source_url=source_url,
                target_url=target_url,
                content_type=ctype,
                object_pk=self.pk,
            )
            log.debug(f"Added new OutgoingWebmention ({obj.pk}): {target_url}")

    def _get_outgoing_urls(self):
        """
        Gets all the outgoing links from the object's HTML.

        Returns an array of unique URLs.
        Only includes URLs that do not link to this page.
        """
        source_url = urldefrag(self.get_absolute_url_with_domain())[0]
        urls = []

        soup = BeautifulSoup(self.get_all_html(), "html.parser")
        raw_urls = [a["href"] for a in soup.find_all("a", href=True)]

        for target_url in raw_urls:
            target_url = urldefrag(target_url)[0]
            if target_url[:8] == "https://" or target_url[:7] == "http://":
                if (
                    urls_are_equal(source_url, target_url, ignore_scheme="http")
                    is False
                ):

                    urls.append(target_url)

        # Get rid of any duplicates:
        return list(set(urls))
