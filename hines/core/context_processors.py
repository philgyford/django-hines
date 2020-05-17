from django.contrib.sites.shortcuts import get_current_site

from hines.core import app_settings
from hines.core.utils import get_site_url


# Things that we want to be available in the context of every page.


def core(request):
    current_site = get_current_site(request)

    show_grid = True if request.GET.get("grid", None) == "1" else False

    return {
        "site_name": current_site.name,
        "site_url": get_site_url(),
        "google_analytics_id": app_settings.GOOGLE_ANALYTICS_ID,
        "show_grid": show_grid,
        "author_name": app_settings.AUTHOR_NAME,
        "author_email": app_settings.AUTHOR_EMAIL,
        "site_icon": app_settings.SITE_ICON,
    }
