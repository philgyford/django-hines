from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500,\
        static
from django.urls import include, path, re_path
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


# These URLs will be in namespaces like 'spectator:reading':
spectator_patterns = ([
    path('spectator/', include('spectator.core.urls.core', namespace='core')),

    path('reading/', include('spectator.reading.urls', namespace='reading')),

    path('creators/', include('spectator.core.urls.creators',
        namespace='creators')),
], 'spectator')


# We might in future have a photos app, in which case we'd include
# its urlconf here. But for now, just one view in the core app:
photos_patterns = ([
    path('', core_views.PhotosHomeView.as_view(), name='home'),
], 'photos')


# All of these will be under the /ROOT_DIR/ directory.
# e.g. /phil/photos/blah/blah/
root_dir_patterns = ([
    path('photos/', include(photos_patterns)),

    path('links/', include('hines.links.urls')),

    path('patterns/', include('hines.patterns.urls')),

    # Redirecting legacy author/publication detail URLs that have ?id=123.
    path('reading/author/', core_views.AuthorRedirectView.as_view()),
    path('reading/publication/', core_views.PublicationRedirectView.as_view()),

    re_path(r'^writing/resources/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<path>.*?)$',
                        core_views.WritingResourcesRedirectView.as_view()),

    path('', include(spectator_patterns)),

    path('', include('hines.core.urls')),

    path('', include('hines.weblogs.urls')),
])

urlpatterns = [

    # REDIRECTS

    path('favicon.ico', RedirectView.as_view(
        url=static_tag('hines/img/favicons/favicon.ico'), permanent=True)),

    path('apple-touch-icon.png', RedirectView.as_view(
        url=static_tag('hines/img/favicons/apple-touch-icon.png'),
        permanent=True)),

    re_path(r'^archive/(?P<path>.*)$',
                                core_views.ArchiveRedirectView.as_view()),

    path('cgi-bin/mt/mt-search.cgi',
                                core_views.MTSearchRedirectView.as_view()),


    # SITEMAP

    path('sitemap.xml', sitemaps_views.index, {'sitemaps': sitemaps}),

    path('sitemap-<slug:section>.xml', sitemaps_views.sitemap,
        {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),


    # ADMIN

    path('backstage/', admin.site.urls),


    # EVERYTHING ELSE

    path('', core_views.HomeView.as_view(), name='home'),

    path('{}/'.format(ROOT_DIR), include(root_dir_patterns)),

    # Used in the weblogs app:
    path('comments/', include('django_comments.urls')),

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
        path('400/', core_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),

        path('403/', core_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),

        path('404/', core_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),

        path('500/', core_views.server_error),
    ]

    urlpatterns += \
        static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
