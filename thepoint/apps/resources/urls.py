from django.urls import path

from . import feeds, views

app_name = 'resources'
urlpatterns = [
    path('',
         views.ResourceList.as_view(),
         name='index'),
    path('tag/<slug:slug>/',
         views.TagList.as_view(),
         name='tag'),
    path('<slug:slug>',
         views.ResourceDetail.as_view(),
         name='detail'),
    path('download/<int:pk>',
         views.AttachmentView.as_view(),
         name='attachment'),
    path('feed/<slug:slug>/art',
         views.FeedArtworkView.as_view(),
         name='feed_artwork'),
    path('feed/<slug:slug>',
         feeds.ResourceFeedRSS(),
         name='rss'),
    path('feed/<slug:slug>/atom',
         feeds.ResourceFeedAtom(),
         name='atom'),
]
