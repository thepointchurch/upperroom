from django.conf.urls import url

from newsletter import views

app_name = 'newsletter'
urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'(?P<slug>\d{4}-\d{2}-\d{2})$',
        views.DetailView.as_view(),
        name='issue'),
]
