import bleach

from django_comments.models import Comment

from . import utils


class CustomComment(Comment):

    class Meta:
        proxy = True
        verbose_name = 'Comment'

    def save(self, *args, **kwargs):
        self.comment = self.clean_comment(self.comment)
        super().save(*args, **kwargs)

    def clean_comment(self, comment):
        """
        Strip disallowed tags, add rel=nofollow to links, remove extra newlines.
        """
        return utils.clean_comment(comment)

