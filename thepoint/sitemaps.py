from itertools import chain

from django.contrib import sitemaps
from django.urls import reverse

from upperroom.resources.models import get_featured_items


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return list(chain(["home"], get_featured_items(), ["resources:index", "contact", "copyright"]))

    def location(self, obj):
        if isinstance(obj, str):
            return reverse(obj)
        return obj.get_absolute_url()
