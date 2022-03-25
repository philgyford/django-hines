from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

from django_comments.models import Comment

from .utils import clean_comment


class CustomComment(Comment):
    class Meta:
        proxy = True
        verbose_name = "Comment"

    def save(self, *args, **kwargs):
        self.comment = self.sanitize_comment(self.comment)
        super().save(*args, **kwargs)

    def sanitize_comment(self, comment):
        """
        Strip disallowed tags, add rel=nofollow to links, remove extra newlines.
        """
        return clean_comment(comment)

    def set_parent_comment_data(self):
        """
        We store the comment_count for each object that can have comments.
        So here we set the comment_count after we save/delete each comment.
        Which should take account of comments being added, removed etc.

        We also have to ensure the parent object's last_comment_time is
        still accurate.

        Called from post_delete and post_save signals.
        """

        # Make sure the content_type and object for this CustomComment exist.
        # This is adapted from django.contrib.contenttypes.views.shortcut().
        try:
            content_type = ContentType.objects.get(pk=self.content_type_id)
            if not content_type.model_class():
                raise AttributeError(
                    "Content type %(ct_id)s object has no associated model"
                    % {"ct_id": self.content_type_id}
                )
            obj = content_type.get_object_for_this_type(pk=self.object_pk)
        except (ObjectDoesNotExist, ValueError):
            raise AttributeError(
                "Content type %(ct_id)s object %(obj_id)s doesn't exist"
                % {"ct_id": self.content_type_id, "obj_id": self.object_pk}
            )

        # All good. So set the count of visible comments.
        # Note: We explicitly remove any ordering because we don't need it
        # and it should speed things up.
        qs = CustomComment.objects.filter(
            content_type__pk=self.content_type_id,
            object_pk=self.object_pk,
            site=self.site,
            is_public=True,
            is_removed=False,
        ).order_by()
        obj.comment_count = qs.count()

        # We also need to set the last_comment_time on the object.
        if obj.comment_count == 0:
            # No comments (this comment must be invisible).
            # So make sure the comment time is None.
            obj.last_comment_time = None
        else:
            # There are some comments on this object...
            if (
                self.is_public is True
                and self.is_removed is False
                and (
                    obj.last_comment_time is None
                    or self.submit_date > obj.last_comment_time
                )
            ):
                # This is the most recent public comment, so:
                obj.last_comment_time = self.submit_date
            else:
                # This isn't the most recent public comment, so:
                obj.last_comment_time = qs.aggregate(Max("submit_date"))[
                    "submit_date__max"
                ]

        obj.save()


# Looking for the Comment Moderator? It's at weblogs.models.PostCommentModerator !
