from django.urls import include, path, register_converter

from hines.core import converters
from . import feeds, views


register_converter(converters.FourDigitYearConverter, 'yyyy')
register_converter(converters.TwoDigitMonthConverter, 'mm')
register_converter(converters.TwoDigitDayConverter, 'dd')


app_name = 'weblogs'

urlpatterns = [

    path('post-tag-autocomplete/', views.PostTagAutocomplete.as_view(),
        name='post_tag_autocomplete',),

    # 2001 version in a pop-up window:
    path('random-phil/', views.RandomPhilView.as_view(), {'set': '2001'}, name='random_phil_2001'),
    # 2002 version in the main window:
    path('random/', views.RandomPhilView.as_view(), {'set': '2002'}, name='random_phil_2002'),

    path(
        '<slug:blog_slug>/<yyyy:year>/<mm:month>/<dd:day>/<slug:post_slug>.php',
        views.PostRedirectView.as_view(),
        name='post_redirect'),

    path('<slug:blog_slug>/', views.BlogDetailView.as_view(),
        name='blog_detail'),

    path('<slug:blog_slug>/archive/', views.BlogArchiveView.as_view(),
        name='blog_archive'),

    path('<slug:blog_slug>/feeds/posts/rss/', feeds.BlogPostsFeedRSS(),
        name='blog_feed_posts_rss'),

    path('<slug:blog_slug>/tags/', views.BlogTagListView.as_view(),
        name='blog_tag_list'),

    path('<slug:blog_slug>/tags/<slug:tag_slug>/',
        views.BlogTagDetailView.as_view(),
        name='blog_tag_detail'),

    path('<slug:blog_slug>/<yyyy:year>/<mm:month>/<dd:day>/<slug:post_slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'),

    path('<slug:blog_slug>/<yyyy:year>/<mm:month>/<dd:day>/',
        views.PostDayArchiveView.as_view(),
        name='post_day_archive'),

    path('<slug:blog_slug>/<yyyy:year>/<mm:month>/',
        views.PostMonthArchiveView.as_view(),
        name='post_month_archive'),

    path('<slug:blog_slug>/<yyyy:year>/', views.PostYearArchiveView.as_view(),
        name='post_year_archive'),
]
