from django.conf.urls.defaults import *
from photos import views


urlpatterns = patterns('',
    (r'^$', views.photos_index, {}, 'photos_index'),

)
