from django.conf.urls import patterns, url

from resources import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.TagList.as_view(
                               template_name='resources/about.html'),
                           {'slug': 'about'},
                           name='about'),
                       )
