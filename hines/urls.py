from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    (r'^cmnt/', include('django.contrib.comments.urls')),
    
    (r'^', include('aggregator.urls')),

    (r'^reading/', include('books.urls')),

    (r'^', include('people.urls')),

    (r'^', include('weblog.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
   )
   

urlpatterns += patterns('',
    (r'^', include('django.contrib.flatpages.urls')),
)
