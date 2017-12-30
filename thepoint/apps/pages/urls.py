from django.conf.urls import url
from django.contrib.flatpages import views

app_name = 'pages'
urlpatterns = [
    url(r'^$',
        views.flatpage,
        {'url': '/'},
        name='home'),
    url(r'^calendar$',
        views.flatpage,
        {'url': '/calendar'},
        name='calendar'),
    url(r'^contact$',
        views.flatpage,
        {'url': '/contact'},
        name='contact'),
    url(r'^copyright$',
        views.flatpage,
        {'url': '/copyright'},
        name='copyright'),
]
