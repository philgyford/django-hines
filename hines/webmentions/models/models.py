from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from hines.core.models import TimeStampedModelMixin


class IncomingWebmention(TimeStampedModelMixin, models.Model):
    """
    A webmention sent from a page on another site (source_url) to
    the target_url on this site.
    """

    # The object whose Detail page the target_url represents.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    source_title = models.CharField(
        blank=True,
        max_length=255,
        help_text="Title of the page that sent the webmention.",
    )
    source_url = models.URLField(
        blank=True,
        help_text="Source address of the HTTP request that sent this webmention.",
        verbose_name="Source URL",
    )
    target_url = models.URLField(
        blank=True,
        help_text="URL of the object on this site that the mention was sent to.",
        verbose_name="Target URL",
    )

    is_public = models.BooleanField(
        default=False, help_text="Allow this to appear publicly"
    )

    source_is_deleted = models.BooleanField(
        default=False, help_text="Has the source page been deleted?"
    )

    is_validated = models.BooleanField(
        default=False,
        help_text="True if both source and target have been validated, "
        "confirmed to exist, and source really does link to target.",
    )

    class Meta:
        ordering = ["-time_created"]

    def set_parent_incoming_webmention_data(self):
        """
        Set the incoming_webmention_count for the object this webmention is on.
        e.g. the Post that is this webmention's target.
        """
        # Make sure the content_type and object for this IncomingWebmention exist.
        # This is adapted from django.contrib.contenttypes.views.shortcut().
        try:
            content_type = ContentType.objects.get(pk=self.content_type_id)
            if not content_type.model_class():
                raise AttributeError(
                    u"Content type %(ct_id)s object has no associated model"
                    % {"ct_id": self.content_type_id}
                )
            obj = content_type.get_object_for_this_type(pk=self.object_pk)
        except (ObjectDoesNotExist, ValueError):
            raise AttributeError(
                u"Content type %(ct_id)s object %(obj_id)s doesn't exist"
                % {"ct_id": self.content_type_id, "obj_id": self.object_pk}
            )

        qs = IncomingWebmention.objects.filter(
            content_type__pk=self.content_type_id,
            object_pk=self.object_pk,
            is_public=True,
            is_validated=True,
        ).order_by()
        obj.incoming_webmention_count = qs.count()
        obj.save()


class OutgoingWebmention(TimeStampedModelMixin, models.Model):
    """
    A webmention sent from a page on this site (source_url) to the
    target_url on another site.
    """

    class Status(models.TextChoices):
        WAITING = "WA", "Waiting to be sent"
        TARGET_UNREACHABLE = "TU", "Target URL is unreachable"
        TARGET_ERROR = "TE", "Target URL returned an error"
        ENDPOINT_UNREACHABLE = "EU", "Endpoint URL is unreachable"
        ENDPOINT_ERROR = "EE", "Endpoint URL returned an error"
        NO_ENDPOINT = "NE", "No endpoint found"
        OK = "OK", "Target accepted the webmention"

    # The object whose Detail page the source_url represents.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_pk")

    source_url = models.URLField(
        blank=True,
        help_text="ULR of the object on this site that sent the webmention.",
        verbose_name="Source URL",
    )

    target_url = models.URLField(
        blank=True, help_text="The URL that was mentioned.", verbose_name="Target URL"
    )

    target_endpoint_url = models.URLField(
        null=True,
        blank=True,
        help_text="The endpoint URL to which we sent the webmention.",
        verbose_name="Target endpoint URL",
    )

    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.WAITING
    )

    target_response_code = models.PositiveIntegerField(
        default=None, null=True, blank=True
    )
    endpoint_response_code = models.PositiveIntegerField(
        default=None, null=True, blank=True
    )

    error_message = models.CharField(max_length=255, blank=True)
    last_attempt_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-time_created"]

    @classmethod
    def get_error_statuses(cls):
        "The Status values which count as errors"
        return [
            cls.Status.TARGET_UNREACHABLE,
            cls.Status.TARGET_ERROR,
            cls.Status.ENDPOINT_UNREACHABLE,
            cls.Status.ENDPOINT_ERROR,
            cls.Status.NO_ENDPOINT,
        ]
