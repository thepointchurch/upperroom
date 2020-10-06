from django.contrib.sites.models import Site
from django.db.models import Prefetch

from .models import ExtendedSite


def site(request):
    current_site = Site.objects.get_current()
    try:
        extended_site = ExtendedSite.objects.prefetch_related(Prefetch("keywords")).get(site=current_site)
    except ExtendedSite.DoesNotExist:
        extended_site = None
    return {
        "site": current_site,
        "extended_site": extended_site,
    }
