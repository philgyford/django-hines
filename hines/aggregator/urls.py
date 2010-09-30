from django.conf.urls.defaults import *
from aggregator.views import aggregator_day, aggregator_index
from weblog.feeds import LatestAllEntriesFeed, LatestAllCommentsFeed

urlpatterns = patterns('',

    (r'^feed/entries/$', LatestAllEntriesFeed(), {}, 'aggregator_entries_feed'),

    (r'^feed/comments/$', LatestAllCommentsFeed(), {}, 'aggregator_comments_feed'),

    (r'^$', aggregator_index, {}, 'aggregator_index'),
        
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', aggregator_day, {}, 'aggregator_day'),

)