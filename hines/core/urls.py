from django.conf.urls import url
from django.contrib.flatpages import views as flatpages_views

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

]

