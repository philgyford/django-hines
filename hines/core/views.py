from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'


class DayArchiveView(TemplateView):
    # All TODO, including all tests.
    template_name = 'core/day_archive.html'

