from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500,\
        include, static, url
from django.contrib import admin
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import views as sitemaps_views
from django.templatetags.static import static as static_tag
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from spectator.core.sitemaps import CreatorSitemap
from spectator.reading import sitemaps as reading_sitemaps

from hines.core import views as core_views
from hines.core.sitemaps import PagesSitemap
from hines.links.sitemaps import BookmarkSitemap
from hines.weblogs.sitemaps import PostSitemap


# e.g. 'phil':
ROOT_DIR = settings.HINES_ROOT_DIR


sitemaps = {
    'pages': PagesSitemap,
    'posts': PostSitemap,
    'flatpages': FlatPageSitemap,
    'publications': reading_sitemaps.PublicationSitemap,
    'publicationseries': reading_sitemaps.PublicationSeriesSitemap,
    'creators': CreatorSitemap,
    'links': BookmarkSitemap,
}


spectator_patterns = [
    url(r'^{}/spectator/'.format(ROOT_DIR),
        include('spectator.core.urls.core', namespace='core')),

    url(r'^{}/reading/'.format(ROOT_DIR),
        include('spectator.reading.urls', namespace='reading')),

    url(r'^{}/creators/'.format(ROOT_DIR),
        include('spectator.core.urls.creators', namespace='creators')),
]


urlpatterns = [

    # REDIRECTS

    url(r'^favicon.ico$', RedirectView.as_view(
        url=static_tag('hines/img/favicons/favicon.ico'), permanent=True)
    ),


    # PAGES

    url(r'^$',
        view=core_views.HomeView.as_view(),
        name='home'
    ),

    # SITEMAP

    url(r'^sitemap\.xml$',
        sitemaps_views.index,
        {'sitemaps': sitemaps}
    ),
    url(r'^sitemap-(?P<section>.+)\.xml$',
        sitemaps_views.sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'
    ),

    url(r'^backstage/', admin.site.urls),

    url(r'^{}/photos/'.format(ROOT_DIR),
        # We might in future have a photos app, in which case we'd include
        # its urlconf here. But for now, just one view in the core app:
        include([
            url(r'^$', core_views.PhotosHomeView.as_view(), name='home'),
        ],
        namespace='photos')
    ),

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

# Use our custom error view so that the error template gets context.
handler400 = core_views.bad_request
handler403 = core_views.permission_denied
handler404 = core_views.page_not_found
handler500 = core_views.server_error


admin.site.site_header = 'Gyford.com admin'


if settings.DEBUG:

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$',
            core_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$',
            core_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$',
            core_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$',
            core_views.server_error),
    ]

    urlpatterns += \
        static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

