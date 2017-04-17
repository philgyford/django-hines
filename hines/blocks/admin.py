from django.contrib import admin
from django import forms

from markdownx.widgets import AdminMarkdownxWidget

from .models import Block


class BlockAdminForm(forms.ModelForm):
    "So we can use Markdownx for a specific Block field."
    class Meta:
        model = Block
        widgets = {
            'content': AdminMarkdownxWidget,
        }
        fields = '__all__'


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'time_modified',)
    search_fields = ('slug', 'title', 'content', )

    form = BlockAdminForm

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

