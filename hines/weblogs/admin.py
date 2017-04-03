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
    list_display = ('blog', 'title', 'is_published', 'is_featured', 'time_published',)
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

    def is_published(self, obj):
        return obj.status == Post.LIVE_STATUS
    is_published.boolean = True
    is_published.short_description = 'Published?'

    def is_featured(self, obj):
        return obj.featured == Post.IS_FEATURED
    is_featured.boolean = True
    is_featured.short_description = 'Featured?'

        
