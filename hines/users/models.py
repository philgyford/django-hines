from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    In case we want to customise the user in future.
    Use this rather than django.contrib.auth.models.User.
    """

    mastodon_account = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        help_text="e.g. @Gargron@mastodon.social",
    )

    @property
    def display_name(self):
        "Shortcut to get the best displayable name of the user."
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
