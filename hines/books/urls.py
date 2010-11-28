from django.conf.urls.defaults import *
from books import views


urlpatterns = patterns('',
    (r'^reading/publication/(?P<publication_id>\d+)/$', views.books_publication, {}, 'books_publication'),

    (r'^reading/(?P<year>\d{4})/$',
        views.reading_archive_year, {}, 'reading_archive_year'),

)
