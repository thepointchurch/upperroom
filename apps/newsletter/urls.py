from django.conf.urls import patterns, url

from newsletter import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.IndexView.as_view(),
                           name='index'),
                       url(r'(?P<slug>\d{4}-\d{2}-\d{2})$',
                           views.DetailView.as_view(),
                           name='issue'),
                       )
