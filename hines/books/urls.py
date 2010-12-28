from django.conf.urls.defaults import *
from books import views


urlpatterns = patterns('',
    (r'^$', views.books_index, {}, 'books_index'),

    (r'^publication/(?P<publication_id>\d+)/$', views.books_publication, {}, 'books_publication'),

    (r'^(?P<year>\d{4})/$',
        views.reading_archive_year, {}, 'reading_archive_year'),

)
