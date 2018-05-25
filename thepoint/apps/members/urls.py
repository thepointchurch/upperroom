from django.contrib import auth
from django.urls import path, reverse_lazy

from . import views

app_name = 'members'
urlpatterns = [
    path('',
         views.IndexView.as_view(),
         name='index'),
    path('login',
         auth.views.login,
         name='login'),
    path('relogin',
         auth.views.logout_then_login,
         name='relogin'),
    path('logout',
         auth.views.logout,
         {'next_page': '/directory/'},
         name='logout'),
    path('passwd',
         views.password_change,
         {'post_change_redirect':
          reverse_lazy('members:index')},
         name='password_change'),
    path('passwd/reset',
         auth.views.password_reset,
         {'post_reset_redirect': 'reset/done'},
         name='password_reset'),
    path('passwd/reset/done',
         auth.views.password_reset_done,
         name='password_reset_done'),
    path('passwd/reset/<uidb64>/<token>',
         auth.views.password_reset_confirm,
         {'post_reset_redirect': '../complete'},
         name='password_reset_confirm'),
    path('passwd/reset/complete',
         auth.views.password_reset_complete,
         name='password_reset_complete'),
    path('create',
         views.CreateView.as_view(),
         name='create'),
    path('create/<int:pk>',
         views.CreateConfirmView.as_view(),
         name='create_confirm'),
]
