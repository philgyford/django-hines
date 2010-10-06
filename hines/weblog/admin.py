import datetime
from django.contrib import admin
from weblog.models import Blog, Entry

class BlogAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('site', 'name', 'short_name', 'description', 'slug', 'sort_order', 'remote_entries_feed_url', 'enable_comments')
        }),
    )
    prepopulated_fields = { 'slug': ['short_name'] }
    
admin.site.register(Blog, BlogAdmin)


class EntryAdmin(admin.ModelAdmin):
    exclude = (
        'author',
    )
    fieldsets = (
        (None, {
            'fields': ('blog', 'title', 'format', 'body', 'body_more', 'excerpt')
        }),
        ('Meta', {
            'fields': ('slug', 'tags', 'remote_url', 'featured',  'status', 'published_date', 'enable_comments', )
        }),
    )
    prepopulated_fields = { 'slug': ['title'] }
    list_display = ('title', 'blog', 'published_date', )
    list_filter = ('blog',)
    search_fields = ['title', 'excerpt', 'body', 'body_more',]
    
    def save_model(self, request, obj, form, change):
        if not change:
            # Saving for the first time, so set the author and created_date.
            obj.author = request.user
        obj.save()

admin.site.register(Entry, EntryAdmin)