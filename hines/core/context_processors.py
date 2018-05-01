from django.contrib.sites.shortcuts import get_current_site
from hines.core import app_settings


# Things that we want to be available in the context of every page.


def core(request):
    current_site = get_current_site(request)

    show_grid = True if request.GET.get('grid', None) == '1' else False

    return {
        'site_name': current_site.name,
        'google_analytics_id': app_settings.GOOGLE_ANALYTICS_ID,
        'show_grid': show_grid,
    }
