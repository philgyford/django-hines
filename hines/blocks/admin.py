from django.contrib import admin

from .models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'time_modified',)
    search_fields = ('slug', 'title', 'content', )

    fieldsets = (
        (None, {
            'fields': ('slug', 'title', 'content',)
        }),
        ('Times', {
            'classes': ('collapse',),
            'fields': ('time_created', 'time_modified',)
        }),
    )

    readonly_fields = ('time_created', 'time_modified', )
