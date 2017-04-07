import bleach

from django_comments.models import Comment

from .utils import clean_comment


class CustomComment(Comment):

    class Meta:
        proxy = True
        verbose_name = 'Comment'

    def save(self, *args, **kwargs):
        self.comment = self.sanitize_comment(self.comment)
        super().save(*args, **kwargs)

    def sanitize_comment(self, comment):
        """
        Strip disallowed tags, add rel=nofollow to links, remove extra newlines.
        """
        return clean_comment(comment)

