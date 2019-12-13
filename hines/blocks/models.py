from django.db import models

from hines.core.models import TimeStampedModelMixin
from hines.core.utils import markdownify


class Block(TimeStampedModelMixin, models.Model):
    "A single block that can be displayed in a template."

    slug = models.SlugField(
        max_length=255, help_text="Used in a template to include this Block."
    )

    title = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        help_text="Optional title for this Block",
    )

    content = models.TextField(blank=False, help_text="Can use HTML or Markdown.")

    content_html = models.TextField(
        blank=True,
        editable=False,
        help_text="Fully HTML version of Content, created on save.",
        verbose_name="Content HTML",
    )

    class Meta:
        ordering = [
            "title",
        ]

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.slug

    def save(self, *args, **kwargs):
        self.content_html = markdownify(self.content)
        super().save(*args, **kwargs)
