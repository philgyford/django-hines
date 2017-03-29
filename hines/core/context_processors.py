from django.contrib.sites.shortcuts import get_current_site


# Things that we want to be available in the context of every page.


def core(request):
    current_site = get_current_site(request)
    return {
        'site_name': current_site.name,
    }

