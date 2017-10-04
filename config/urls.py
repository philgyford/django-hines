from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

from hines.core import views as core_views


# e.g. 'phil':
ROOT_DIR = settings.HINES_ROOT_DIR


spectator_patterns = [
    url(r'^{}/spectator/'.format(ROOT_DIR),
        include('spectator.core.urls.core', namespace='core')),

    url(r'^{}/reading/'.format(ROOT_DIR),
        include('spectator.reading.urls', namespace='reading')),

    url(r'^{}/creators/'.format(ROOT_DIR),
        include('spectator.core.urls.creators', namespace='creators')),
]


urlpatterns = [

    url(r'^$',
        view=core_views.HomeView.as_view(),
        name='home'
    ),

    url(r'^backstage/', admin.site.urls),

    url(r'^{}/links/'.format(ROOT_DIR),
        include('hines.links.urls', namespace='pinboard')),

    # So these URLs will be in namespaces like 'spectator:reading':
    url(r'^',
        include (spectator_patterns, namespace='spectator')),

    url(r'^{}/'.format(ROOT_DIR),
        include('hines.core.urls', namespace='hines')),

    # Used in the weblogs app for the Admin:
    url(r'^markdownx/', include('markdownx.urls')),

    # Used in the weblogs app:
    url(r'^comments/', include('django_comments.urls')),
]


admin.site.site_header = 'Gyford.com admin'


if settings.DEBUG:

    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += \
        static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += \
        static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

