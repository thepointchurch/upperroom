from itertools import chain

from django.contrib import sitemaps
from django.urls import reverse

from resources.models import get_featured_items


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return list(chain(
            ['pages:home'],
            get_featured_items(),
            ['resources:index',
             'pages:contact',
             'pages:copyright'],
        ))

    def location(self, item):
        if isinstance(item, str):
            return reverse(item)
        else:
            return item.get_absolute_url()
