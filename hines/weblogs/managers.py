from django.db import models


class PublicPostsManager(models.Manager):
    """
    Returns Posts that have been published.
    """
    def get_queryset(self):
        from .models import Post
        return super().get_queryset().filter(status=Post.Status.LIVE)

