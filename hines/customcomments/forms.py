from django import forms
from django.contrib.comments.forms import CommentForm
from customcomments.models import CommentOnEntry
#from weblog.models import Blog


class CommentFormWithBlog(CommentForm):
    #blog = forms.CharField(widget=forms.HiddenInput)
    #blog = forms.CharField(max_length=200)
    #title = forms.CharField(max_length=200)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CommentOnEntry

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the blog field
        data = super(CommentFormWithBlog, self).get_comment_create_data()
        # Get the Blog that this comment's target_object (an Entry) is associated with.
        #data['blog'] = self.target_object.blog
        #data['title'] = self.cleaned_data['title']
        
        return data
