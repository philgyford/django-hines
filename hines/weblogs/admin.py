from dal import autocomplete

from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse_lazy

from markdownx.widgets import AdminMarkdownxWidget

from hines.core.utils import datetime_now
from .models import Blog, Post, Trackback


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order',)
    search_fields = ('name', 'short_name', )

    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'slug', 'sort_order',
                        'allow_comments',)
        }),
        ('Feed', {
            'fields': ('feed_title', 'feed_description',
                        'show_author_email_in_feed',)
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('time_created', 'time_modified',)


class PostAdminForm(autocomplete.FutureModelForm):
    """
    So we can use Markdownx for two specific Post fields.
    And add custom validation.
    """
    class Meta:
        model = Post
        widgets = {
            'intro': AdminMarkdownxWidget,
            'body': AdminMarkdownxWidget,
            # The django-autocomplete-light tag widget:
            'tags': autocomplete.TaggitSelect2(
                                reverse_lazy('weblogs:post_tag_autocomplete')),
        }
        fields = '__all__'

    def clean(self):
        """
        A Post that's Scheduled should have a time_published that's in the future.
        """
        status = self.cleaned_data.get('status')
        time_published = self.cleaned_data.get('time_published')

        if status == Post.SCHEDULED_STATUS:
            if time_published == None:
                raise forms.ValidationError("If this post is Scheduled it should have a Time Published.")
            elif time_published <= datetime_now():
                raise forms.ValidationError("This post is Scheduled but its Time Published is in the past.")
        return self.cleaned_data


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('blog', 'title', 'is_published', 'time_published',
                    'is_featured', )
    list_display_links = ('title',)
    list_filter = ('blog', 'time_published', 'status', 'featured',)
    search_fields = ('title', 'excerpt', 'intro', 'body', )
    date_hierarchy = 'time_published'

    form = PostAdminForm

    fieldsets = (
        (None, {
            'fields': ('blog', 'author', 'title', 'slug', 'status',
                        'time_published', 'featured',)
        }),
        ('The post', {
            'fields': ('html_format', 'intro', 'body', 'excerpt', 'remote_url',
                'tags',),
        }),
        ('Comments', {
            'fields': ('allow_comments', 'comment_count', 'last_comment_time',
                        'trackback_count',),
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    prepopulated_fields = {'slug': ('title',)}
    radio_fields = {'featured': admin.HORIZONTAL}
    readonly_fields = ('time_created', 'time_modified', )

    def is_published(self, obj):
        return obj.status == Post.LIVE_STATUS
    is_published.boolean = True
    is_published.short_description = 'Published?'

    def is_featured(self, obj):
        return obj.featured == Post.IS_FEATURED
    is_featured.boolean = True
    is_featured.short_description = 'Featured?'


@admin.register(Trackback)
class TrackbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog_name', 'post', 'time_created',
                    'is_visible', )
    list_display_links = ('title',)
    search_fields = ('title', 'excerpt',)
    date_hierarchy = 'time_created'

    fieldsets = (
        (None, {
            'fields': ('post', 'blog_name', 'title', 'excerpt', 'url',
                        'ip_address', 'is_visible',)
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    raw_id_fields = ('post',)
    readonly_fields = ('time_created', 'time_modified', )
