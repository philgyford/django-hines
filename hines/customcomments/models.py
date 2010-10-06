from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
#from weblog.models import Blog

class CommentOnEntry(Comment):
    """
    Wrapping the default Comment class for comments posted to blog Entries. 
    Lets us tie each Comment to a particular Blog, which makes some things -- like lists of Comments on a Blog -- much easier.
    """
    #blog = models.ForeignKey(Blog)
    #title = models.CharField(max_length=200)
    
    objects = CommentManager()