from django.contrib.sites.models import Site


def site(request):
    current_site = Site.objects.get_current()
    return {
        "site": current_site,
        "extended_site": getattr(current_site, "extra", None),
    }
