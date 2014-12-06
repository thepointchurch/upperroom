from django.views import generic

from directory.models import Person
from roster.models import Meeting, Role


class MeetingIndex(generic.ListView):
    model = Meeting
    allow_future = True
    template_name = 'roster/index.html'

    def get_queryset(self):
        return Meeting.current_objects.all()[:5]


class MonthlyMeetingView(generic.MonthArchiveView):
    model = Meeting
    allow_future = True
    date_field = 'date'
    make_object_list = True


class PersonList(generic.ListView):
    model = Role
    template_name = 'roster/person_list.html'

    def get_queryset(self):
        self.person = self.kwargs['pk']
        return Role.current_objects.filter(person__id=self.person)

    def get_context_data(self, **kwargs):
        context = super(PersonList, self).get_context_data(**kwargs)
        context['person'] = Person.objects.get(id=self.person)
        return context


class PersonTaskList(PersonList):
    template_name = 'roster/person_task.ics'
    content_type = 'text/calendar'


class PersonEventList(PersonList):
    template_name = 'roster/person_event.ics'
    content_type = 'text/calendar'
