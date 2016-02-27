from django.conf.urls import url

from directory import views


app_name = 'directory'
urlpatterns = [
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^(?P<letter>[a-z])$',
        views.LetterView.as_view(),
        name='letter'),
    url(r'^(?P<pk>\d+)$',
        views.DetailView.as_view(),
        name='detail'),
    url(r'^search$',
        views.SearchView.as_view(),
        name='search'),
    url(r'^edit$',
        views.FamilyEditView.as_view(),
        name='edit'),
    url(r'^birthdays$',
        views.BirthdayView.as_view(),
        name='birthdays'),
    url(r'^anniversaries$',
        views.AnniversaryView.as_view(),
        name='anniversaries'),
    url(r'^pdf$',
        views.PdfView.as_view(),
        name='pdf'),
]
