from django.urls import include, path, register_converter
from django.contrib.flatpages import views as flatpages_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import converters, feeds
from . import views as core_views


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitMonthConverter, 'mm')
register_converter(converters.TwoDigitDayConverter, 'dd')


app_name = 'hines'

urlpatterns = [

    # Send anyone going to '/phil/' to the home page at '/'.
    path('', RedirectView.as_view(url='/', permanent=False)),

    path('feeds/everything/rss/', feeds.EverythingFeedRSS(),
        name='everything_feed_rss'),

    path('patterns/', include('hines.patterns.urls')),


    # Flatpages with names:

    path('about/', flatpages_views.flatpage,
        {'url': '/phil/about/'}, name='about'),

    path('archive/', flatpages_views.flatpage,
        {'url': '/phil/archive/'}, name='archive'),

    path('work/', flatpages_views.flatpage,
        {'url': '/phil/work/'}, name='about_work'),

    path('timeline/', flatpages_views.flatpage,
        {'url': '/phil/timeline/'}, name='timeline'),

    path('misc/', flatpages_views.flatpage,
        {'url': '/phil/misc/'}, name='misc'),

    path('feeds/', flatpages_views.flatpage,
        {'url': '/phil/feeds/'}, name='feeds'),


    path('<yyyy:year>/<mm:month>/<dd:day>/',
        core_views.DayArchiveView.as_view(), name='day_archive'),

    path('', include('hines.weblogs.urls')),
]

