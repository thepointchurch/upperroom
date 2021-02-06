from django.urls import path

from . import views

app_name = "weblog"
urlpatterns = [
    path("", views.WeblogList.as_view(), name="index"),
    path("<int:year>/<int:month>/<slug:slug>", views.WeblogDetail.as_view(), name="detail"),
    path("download/<uuid:pk>", views.AttachmentView.as_view(), name="attachment"),
]
