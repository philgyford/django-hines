from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin


spectator_patterns = [

    url(r'^phil/spectator/', include('spectator.core.urls.core', namespace='core')),

    url(r'^phil/reading/', include('spectator.reading.urls', namespace='reading')),

    url(r'^phil/creators/', include('spectator.core.urls.creators', namespace='creators')),

]

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # So these URLs will be in namespaces like 'spectator:reading':
    url(r'^', include (spectator_patterns, namespace='spectator')),

    url(r'^phil/', include('hines.core.urls', namespace='hines')),

    # Used in the weblogs app for the Admin:
    url(r'^markdownx/', include('markdownx.urls')),

    # Used in the weblogs app:
    url(r'^comments/', include('django_comments.urls')),
]


if settings.DEBUG:

    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += \
        static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += \
        static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

