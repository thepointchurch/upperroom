from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from .models import Meeting, Role
from ..directory.models import Person
from ..utils.mixin import NeverCacheMixin


class MeetingIndex(LoginRequiredMixin, generic.ListView):
    model = Meeting
    allow_future = True
    template_name = 'roster/index.html'

    def get_queryset(self):
        return Meeting.current_objects.all()[:5]


class MonthlyMeetingView(LoginRequiredMixin, generic.MonthArchiveView):
    model = Meeting
    allow_future = True
    date_field = 'date'
    make_object_list = True


class PublicPersonList(generic.ListView):
    model = Role
    template_name = 'roster/person_list.html'

    def get_queryset(self):
        self.person = self.kwargs['pk']
        return Role.current_objects.filter(people__id=self.person)

    def get_context_data(self, **kwargs):
        context = super(PublicPersonList, self).get_context_data(**kwargs)
        context['person'] = Person.objects.get(id=self.person)
        return context


class PersonList(LoginRequiredMixin, PublicPersonList):
    pass


class PersonTaskList(NeverCacheMixin, PublicPersonList):
    template_name = 'roster/person_task.ics'
    content_type = 'text/calendar'


class PersonEventList(NeverCacheMixin, PublicPersonList):
    template_name = 'roster/person_event.ics'
    content_type = 'text/calendar'
