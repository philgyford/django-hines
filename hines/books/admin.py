from django.contrib import admin
from django.contrib import gis 
from books.models import Publication, Reading, Role, Series

class RoleInline(admin.TabularInline):
    model = Role
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('person', 'name', 'publication',)
        }),
    )

class ReadingInline(admin.TabularInline):
    model = Reading
    extra = 1
    fieldsets = (
        (None, {
            # Add 'start_date_granularity', 'end_date_granularity' if you need to edit them.
            'fields': ('start_date', 'end_date', 'finished',)
        }),
    )


class PublicationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('series', 'name', 'home_url', 'notes_url')
        }),
        ('ISBN', {
            'fields': (('isbn_uk', 'isbn_us',),)
        })
    )
    inlines = (RoleInline, ReadingInline,)
    list_display = ('__unicode__', 'authors_names',)
admin.site.register(Publication, PublicationAdmin)


class ReadingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('publication', 'start_date', ('end_date', 'finished',),)
        }),
        ('Granularity', {
            'fields': ('start_date_granularity', 'end_date_granularity',),
            'classes': ['collapse',],
        }),
    )
    list_display = ('publication', 'start_date', 'end_date',)
    list_filter = ('start_date', 'end_date', 'finished',)
admin.site.register(Reading, ReadingAdmin)


class SeriesAdmin(admin.ModelAdmin):
    pass
admin.site.register(Series, SeriesAdmin)



