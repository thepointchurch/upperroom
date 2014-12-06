from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
                       url(r'^directory/',
                           include('directory.urls', namespace='directory')),
                       url(r'^library/',
                           include('library.urls', namespace='library')),
                       url(r'^members/',
                           include('members.urls', namespace='members',
                                   app_name='members')),
                       url(r'^poi/',
                           include('newsletter.urls', namespace='poi',
                                   app_name='newsletter')),
                       url(r'^roster/',
                           include('roster.urls', namespace='roster')),

                       url(r'^admin/', include(admin.site.urls)),

                       url(r'', include('pages.urls', namespace='pages')),
                       )
