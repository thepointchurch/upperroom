from django.conf.urls import patterns, url
from django.contrib import flatpages

urlpatterns = patterns('',
    url(r'^$', flatpages.views.flatpage, {'url': '/'}, name='home'),
    url(r'^calendar/$', flatpages.views.flatpage, {'url': '/calendar/'}, name='calendar'),
    url(r'^contact/$', flatpages.views.flatpage, {'url': '/contact/'}, name='contact'),
    url(r'^copyright/$', flatpages.views.flatpage, {'url': '/copyright/'}, name='copyright'),
)
