from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.PatternsView.as_view(),
        name='pattern_list'),

    url(r'^(?P<slug>[\w-]+)/$',
        views.PatternsView.as_view(),
        name='pattern_detail'),
]
