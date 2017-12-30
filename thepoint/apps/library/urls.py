from django.conf.urls import url

from . import views


app_name = 'library'
urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^search$',
        views.SearchView.as_view(),
        name='search'),
]
