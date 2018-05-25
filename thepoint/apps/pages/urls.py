from django.contrib.flatpages import views
from django.urls import path

app_name = 'pages'
urlpatterns = [
    path('',
         views.flatpage,
         {'url': '/'},
         name='home'),
    path('calendar',
         views.flatpage,
         {'url': '/calendar'},
         name='calendar'),
    path('contact',
         views.flatpage,
         {'url': '/contact'},
         name='contact'),
    path('copyright',
         views.flatpage,
         {'url': '/copyright'},
         name='copyright'),
]
