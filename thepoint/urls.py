from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('directory/', include('thepoint.apps.directory.urls', namespace='directory')),
    path('library/', include('thepoint.apps.library.urls', namespace='library')),
    path('members/', include('thepoint.apps.members.urls', namespace='members')),
    path('poi/', include('thepoint.apps.newsletter.urls', namespace='poi')),
    path('resources/', include('thepoint.apps.resources.urls', namespace='resources')),
    path('roster/', include('thepoint.apps.roster.urls', namespace='roster')),

    path('admin/', admin.site.urls),

    path('robots.txt', include('robots.urls')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    path('', include('thepoint.apps.pages.urls', namespace='pages')),
]
