from django.conf.urls import include, url
from django.contrib.flatpages import views as flatpages_views
from django.views.generic import TemplateView

from . import views


urlpatterns = [
    url(
        regex=r"^$",
        view=views.HomeView.as_view(),
        name='home'
    ),

    # Flatpages
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
        view=views.DayArchiveView.as_view(),
        name='day_archive'
    ),

    # So we can test these templates when DEBUG=True.
    url(r'^400/$', TemplateView.as_view(template_name='400.html')),
    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),

    url(r'^', include('hines.weblogs.urls')),

]

