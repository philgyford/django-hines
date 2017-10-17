from django.conf.urls import include, url
from django.contrib.flatpages import views as flatpages_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import feeds
from . import views as core_views


urlpatterns = [

    # Send anyone going to '/phil/' to the home page at '/'.
    url(
        regex=r"^$",
        view=RedirectView.as_view(url='/', permanent=False)
    ),

    url(
        regex=r"^feeds/everything/$",
        view=feeds.EverythingFeed(),
        name='everything_feed'
    ),

    # Flatpages with names:
    url(r'^about/$', flatpages_views.flatpage, {'url': '/about/'},
                                                                name='about'),
    url(r'^work/$', flatpages_views.flatpage, {'url': '/work/'},
                                                            name='about_work'),
    url(r'^timeline/$', flatpages_views.flatpage, {'url': '/timeline/'},
                                                            name='timeline'),
    url(r'^misc/$', flatpages_views.flatpage, {'url': '/misc/'},
                                                            name='misc'),

    url(
        # /2016/04/18/twitter/favorites
        regex=r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
        view=core_views.DayArchiveView.as_view(),
        name='day_archive'
    ),

    url(r'^', include('hines.weblogs.urls')),
]

