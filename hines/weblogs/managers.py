from django.db import models


class PublicPostsManager(models.Manager):
    """
    Returns Posts that have been published.
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=self.model.Status.LIVE)
