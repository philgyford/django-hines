from customcomments.models import CommentOnEntry
from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.contrib.comments.models import Comment
from django.contrib.admin.sites import NotRegistered

try:
    admin.site.unregister(Comment)
except NotRegistered:
    pass
    
class CommentsOnEntryAdmin(CommentsAdmin):
    pass
    
admin.site.register(CommentOnEntry, CommentsOnEntryAdmin)