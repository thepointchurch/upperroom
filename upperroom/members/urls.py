from csp.decorators import csp_update
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.urls import path, reverse_lazy
from django.views.decorators.cache import never_cache

from . import views

app_name = "members"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("login", auth.views.LoginView.as_view(), name="login"),
    path("relogin", auth.views.logout_then_login, name="relogin"),
    path("logout", auth.views.LogoutView.as_view(next_page=reverse_lazy("home")), name="logout"),
    path(
        "passwd",
        never_cache(
            csp_update({"script-src": ["'unsafe-inline'"]})(
                user_passes_test(views.not_a_guest)(
                    auth.views.PasswordChangeView.as_view(success_url=reverse_lazy("members:index"))
                )
            )
        ),
        name="password_change",
    ),
    path(
        "passwd/reset",
        never_cache(auth.views.PasswordResetView.as_view(success_url="reset/done")),
        name="password_reset",
    ),
    path("passwd/reset/done", never_cache(auth.views.PasswordResetDoneView.as_view()), name="password_reset_done"),
    path(
        "passwd/reset/<uidb64>/<token>",
        auth.views.PasswordResetConfirmView.as_view(success_url="../complete"),
        name="password_reset_confirm",
    ),
    path(
        "passwd/reset/complete",
        never_cache(auth.views.PasswordResetCompleteView.as_view()),
        name="password_reset_complete",
    ),
    path("create", views.CreateView.as_view(), name="create"),
    path("create/<int:pk>", views.CreateConfirmView.as_view(), name="create_confirm"),
    path("tech", views.TechDetailsView.as_view(), name="tech"),
]
