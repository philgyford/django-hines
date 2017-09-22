from django.contrib import admin
from django.db import models
from django import forms

from markdownx.widgets import AdminMarkdownxWidget

from .models import Blog, Post


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


class PostAdminForm(forms.ModelForm):
    "So we can use Markdownx for two specific Post fields."
    class Meta:
        model = Post
        widgets = {
            'intro': AdminMarkdownxWidget,
            'body': AdminMarkdownxWidget,
        }
        fields = '__all__'


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
                        'time_published', 'featured', 'allow_comments',)
        }),
        ('The post', {
            'fields': ('html_format', 'intro', 'body', 'excerpt', 'remote_url',
                'tags',),
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


