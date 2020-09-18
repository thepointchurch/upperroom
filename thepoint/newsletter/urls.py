from django.urls import path, re_path

from . import views

app_name = "newsletter"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    re_path(r"(?P<slug>\d{4}-\d{2}-\d{2})$", views.DetailView.as_view(), name="issue"),
]
