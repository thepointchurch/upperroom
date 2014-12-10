from django.conf.urls import patterns, url

from resources import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.ResourceList.as_view(),
                           name='index'),
                       url(r'^tag/(?P<slug>[-_\w]+)/$',
                           views.TagList.as_view(),
                           name='tag'),
                       url(r'^(?P<slug>[-_\w]+)/$',
                           views.ResourceDetail.as_view(),
                           name='detail'),
                       url(r'^download/(?P<pk>\d+)/$',
                           views.AttachmentView.as_view(),
                           name='attachment'),
                       )
