from django.urls import path, re_path

from . import views

app_name = "directory"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    re_path(r"^(?P<letter>[a-z])$", views.LetterView.as_view(), name="letter"),
    path("<int:pk>", views.DetailView.as_view(), name="detail"),
    path("search", views.SearchView.as_view(), name="search"),
    path("edit", views.FamilyEditView.as_view(), name="edit"),
    path("birthdays", views.BirthdayView.as_view(), name="birthdays"),
    path("anniversaries", views.AnniversaryView.as_view(), name="anniversaries"),
    path("photo/<int:pk>.jpg", views.FamilyPhotoView.as_view(), name="photo"),
    path("thumbnail/<int:pk>.jpg", views.FamilyPhotoView.as_view(), name="thumbnail"),
    path("contacts.vcf", views.PersonVcardList.as_view(), name="vcard"),
    path("pdf", views.PdfView.as_view(), name="pdf"),
    path("print", views.PrintView.as_view(), name="print"),
]
