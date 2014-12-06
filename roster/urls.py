from django.conf.urls import patterns, url

from roster import views

urlpatterns = patterns('',
                       url(r'^$',
                           views.MeetingIndex.as_view(),
                           name='index'),
                       url(r'^(?P<year>\d{4})/(?P<month>\d+)/$',
                           views.MonthlyMeetingView.as_view(month_format='%m'),
                           name='meeting_month'),
                       url(r'^person/(?P<pk>\d+)/$',
                           views.PersonList.as_view(),
                           name='person'),
                       url(r'^event/(?P<pk>\d+).ics$',
                           views.PersonEventList.as_view(),
                           name='event'),
                       url(r'^task/(?P<pk>\d+).ics$',
                           views.PersonTaskList.as_view(),
                           name='task'),
                       )
