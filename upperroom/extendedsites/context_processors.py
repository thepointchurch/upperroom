from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import Prefetch
from django.templatetags.static import static

from ..utils.markdown import unmarkdown
from .models import ExtendedSite


def site(request):
    current_site = Site.objects.get_current()
    try:
        extended_site = ExtendedSite.objects.prefetch_related(Prefetch("keywords")).get(site=current_site)
    except ExtendedSite.DoesNotExist:
        extended_site = None
    context = {
        "site": current_site,
        "extended_site": extended_site,
        "metadata_description": None,
        "metadata_image": None,
        "metadata_title": current_site.name,
        "metadata_type": "website",
    }
    if extended_site and extended_site.subtitle:
        context["metadata_description"] = unmarkdown(extended_site.subtitle)
    try:
        if settings.SITE_METADATA_IMAGE:
            image = settings.SITE_METADATA_IMAGE
            if not image.startswith("http") or not image.startswith("//"):
                image = static(image)
            context["metadata_image"] = image
    except AttributeError:
        pass
    return context
