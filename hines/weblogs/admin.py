from django.contrib import admin

from .models import Blog, Post


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order',)
    search_fields = ('name', 'short_name', )

    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'slug', 'sort_order')
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('time_created', 'time_modified',)



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('blog', 'title', 'status', 'featured', 'time_published',)
    list_display_links = ('title',)
    search_fields = ('title', 'excerpt', 'intro', 'body', )
    date_hierarchy = 'time_published'

    fieldsets = (
        (None, {
            'fields': ('blog', 'author', 'title', 'slug', 'status',
                        'time_published', 'featured',)
        }),
        ('The post', {
            'fields': ('html_format', 'intro', 'body', 'excerpt', 'remote_url'),
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    prepopulated_fields = {'slug': ('title',)}
    radio_fields = {'featured': admin.HORIZONTAL}
    readonly_fields = ('time_created', 'time_modified', 'time_published',)

