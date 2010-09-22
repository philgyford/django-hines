from django.conf.urls.defaults import *
from weblog.feeds import LatestBlogEntriesFeed
from weblog.views import weblog_archive_month, weblog_blog_index, weblog_entry_detail

urlpatterns = patterns('',

    (r'^(?P<blog_slug>[-\w]+)/$', weblog_blog_index, {}, 'weblog_blog_index'),
    
    (r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/$',
        weblog_archive_month, {}, 'weblog_entry_archive_month'),
    
    (r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        weblog_entry_detail, {}, 'weblog_entry_detail'),
    
    (r'^(?P<blog_slug>[-\w]+)/feed/$', LatestBlogEntriesFeed(), {}, 'weblog_entries_feed'),
    
)