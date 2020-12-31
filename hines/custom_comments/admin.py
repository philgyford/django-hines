from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django_comments import get_model
from django_comments.admin import CommentsAdmin
from django_comments.models import CommentFlag

from .models import CustomComment
from hines.weblogs.models import Post


class CommentFlagInline(admin.TabularInline):
    model = CommentFlag
    extra = 0
    raw_id_fields = ("user",)


class CustomCommentAdmin(CommentsAdmin):
    inlines = [
        CommentFlagInline,
    ]

    def flag(self, obj):
        flag_name = ""
        try:
            flag_name = obj.flags.values().last()["flag"]
        except IndexError:
            pass
        return flag_name

    def post_title(self, obj):
        """
        Return the title of the Post this comment was posted on.
        """
        # I think this was working, to get the ContentType of a Post, but in
        # tests it failed, as ContentType IDs were always different:
        # ct = ContentType.objects.get_for_id(obj.content_type_id)
        # So we now do this and assume all Comments are on Posts:
        ct = ContentType.objects.get_for_model(Post)
        # Get the Post this comment was on:
        post_obj = ct.get_object_for_this_type(pk=obj.object_pk)
        return post_obj.title

    list_display = (
        "name",
        "post_title",
        "ip_address",
        "submit_date",
        "flag",
        "is_public",
        "is_removed",
    )
    list_filter = ("submit_date", "site", "is_public", "is_removed", "flags__flag")


if get_model() is CustomComment:
    admin.site.register(CustomComment, CustomCommentAdmin)
