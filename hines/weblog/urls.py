from django.conf.urls.defaults import *
from weblog.feeds import LatestBlogEntriesFeed
from weblog import views


urlpatterns = patterns('',

    (r'^(?P<blog_slug>[-\w]+)/$', views.weblog_blog_index, {}, 'weblog_blog_index'),
    
    (r'^(?P<blog_slug>[-\w]+)/archive/$', views.weblog_blog_archive, {}, 'weblog_blog_archive'),
    
    (r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/$',
        views.weblog_archive_year, {}, 'weblog_entry_archive_year'),
    
    (r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/$',
        views.weblog_archive_month, {}, 'weblog_entry_archive_month'),
        
    (r'^(?P<blog_slug>[-\w]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        views.weblog_entry_detail, {}, 'weblog_entry_detail'),

    (r'^(?P<blog_slug>[-\w]+)/feed/$', LatestBlogEntriesFeed(), {}, 'weblog_entries_feed'),
    
    (r'^(?P<blog_slug>[-\w]+)/(?P<tag_slug>[-\w]+)/$', views.weblog_tag, {}, 'weblog_tag'),
)