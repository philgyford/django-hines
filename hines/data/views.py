from django.http import Http404
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'data/home.html'
