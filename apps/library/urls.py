from django.conf.urls import patterns, url

from library import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.IndexView.as_view(),
                           name='index'),
                       url(r'^search/$',
                           views.SearchView.as_view(),
                           name='search'),
                       )
