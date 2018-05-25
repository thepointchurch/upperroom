from django.urls import path

from . import views

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
]
