from django.conf.urls import patterns, include, url
from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    url(r'^directory/', include('directory.urls', namespace='directory')),
    url(r'^roster/', include('roster.urls', namespace='roster')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
