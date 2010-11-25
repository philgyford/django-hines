from django.conf.urls.defaults import *
from people import views

urlpatterns = patterns('',

    (r'^person/(?P<person_id>\d+)/$', views.people_person, {}, 'people_person'),

)
