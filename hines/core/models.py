from django.db import models


class TimeStampedModelMixin(models.Model):
    "Should be mixed in to all models."
    time_created = models.DateTimeField(
        auto_now_add=True, help_text="The time this item was created in the database."
    )
    time_modified = models.DateTimeField(
        auto_now=True, help_text="The time this item was last saved to the database."
    )

    class Meta:
        abstract = True
