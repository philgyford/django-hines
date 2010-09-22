from django.contrib import admin
from aggregator.models import Aggregator

class AggregatorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Aggregator, AggregatorAdmin)
