from django.contrib import sitemaps
from django.core.urlresolvers import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    def items(self):
        return ['pages:home',
                'hilight:about',
                'resources:index',
                'pages:contact',
                'pages:copyright']

    def location(self, item):
        return reverse(item)
