from csp.decorators import csp_update
from django.urls import path

from . import views

app_name = "roster"
urlpatterns = [
    path("", views.MeetingIndex.as_view(), name="index"),
    path("<int:year>/<int:month>", views.MonthlyMeetingView.as_view(month_format="%m"), name="meeting_month"),
    path("<int:year>/pdf", views.RosterPdf.as_view(), name="pdf"),
    path("<int:year>/pdf/<int:week_day>", views.RosterPdf.as_view(), name="pdf"),
    path("person/<int:pk>", views.PersonList.as_view(), name="person"),
    path("event/<int:pk>.ics", views.PersonEventList.as_view(), name="event"),
    path("task/<int:pk>.ics", views.PersonTaskList.as_view(), name="task"),
    path("builder", csp_update(SCRIPT_SRC="'unsafe-inline'")(views.BuilderView.as_view()), name="builder"),
]
