from django.urls import path

from . import views

app_name = 'roster'
urlpatterns = [
    path('',
         views.MeetingIndex.as_view(),
         name='index'),
    path('<int:year>/<int:month>',
         views.MonthlyMeetingView.as_view(month_format='%m'),
         name='meeting_month'),
    path('person/<int:pk>',
         views.PersonList.as_view(),
         name='person'),
    path('event/<int:pk>.ics',
         views.PersonEventList.as_view(),
         name='event'),
    path('task/<int:pk>.ics',
         views.PersonTaskList.as_view(),
         name='task'),
]
