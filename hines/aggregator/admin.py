from django.contrib import admin
from aggregator.models import Aggregator

class AggregatorAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('site',)
        }),
        ('Feeds', {
            'fields': ('remote_entries_feed_url', 'remote_comments_feed_url'),
        }),
        ('Comments', {
            'fields': ('enable_comments', 'send_comment_emails_public', 'send_comment_emails_nonpublic', 'allowed_comment_tags', 'test_comments_for_spam', 'typepad_antispam_api_key', 'akismet_api_key')
        }),
    )
admin.site.register(Aggregator, AggregatorAdmin)
