from django.conf.urls import patterns, url

from resources import views

urlpatterns = patterns('',
                       url(r'^about/$',
                           views.TagList.as_view(
                               template_name='resources/about.html'),
                           {'slug': 'about'},
                           name='about'),
                       url(r'^theophilus/$',
                           views.ResourceDetail.as_view(),
                           {'slug': 'theophilus'},
                           name='theophilus'),
                       )
