from django.conf.urls import url
from django.contrib import auth
from django.core.urlresolvers import reverse_lazy

from members import views

app_name = 'members'
urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^login$',
        auth.views.login,
        name='login'),
    url(r'^relogin$',
        auth.views.logout_then_login,
        name='relogin'),
    url(r'^logout$',
        auth.views.logout,
        {'next_page': '/directory/'},
        name='logout'),
    url(r'^passwd$',
        views.password_change,
        {'post_change_redirect':
         reverse_lazy('members:index')},
        name='password_change'),
    url(r'^passwd/reset$',
        auth.views.password_reset,
        {'post_reset_redirect': 'reset/done'},
        name='password_reset'),
    url(r'^passwd/reset/done$',
        auth.views.password_reset_done,
        name='password_reset_done'),
    url(r'^passwd/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        auth.views.password_reset_confirm,
        {'post_reset_redirect': '../complete'},
        name='password_reset_confirm'),
    url(r'^passwd/reset/complete$',
        auth.views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^create$',
        views.CreateView.as_view(),
        name='create'),
    url(r'^create/(?P<pk>\d+)$',
        views.CreateConfirmView.as_view(),
        name='create_confirm'),
]
