from django.contrib import admin
from django.contrib import gis 
from movies.models import Cinema, Movie, Viewing


class ViewingInline(admin.TabularInline):
    model = Viewing
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('cinema', 'view_date', 'cost',)
        }),
    )

class CinemaAdmin(admin.ModelAdmin):
    # list_display seems to do nothing when we're using OSMGeoAdmin...
    list_display = ('__unicode__', 'country',)
    list_filter = ('name',)
gis.admin.site.register(Cinema, gis.admin.OSMGeoAdmin)


class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'year',)
    list_filter = ('year',)
    inlines = (ViewingInline,)
admin.site.register(Movie, MovieAdmin)


class ViewingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('movie', 'cinema', 'view_date', 'cost',)
        }),
    )
    list_display = ('movie', 'view_date', 'cinema',)
    list_filter = ('view_date',)
admin.site.register(Viewing, ViewingAdmin)
