import io

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import FileResponse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from weasyprint import HTML

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


class RosterPdf(generic.TemplateView):
    template_name = "roster/pdf.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get('year')
        week_day = self.kwargs.get('week_day', 1)  # Sunday

        context = super(RosterPdf, self).get_context_data(**kwargs)
        context['site_name'] = get_current_site(None).name
        context['contact_email'] = settings.ROSTER_EMAIL
        context['year'] = year
        context['meeting_list'] = Meeting.objects.all().filter(date__year=year,
                                                               date__week_day=week_day)
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(RosterPdf, self).render_to_response(context, **response_kwargs)
        return FileResponse(io.BytesIO(HTML(string=response.render().content, encoding='utf-8').write_pdf()),
                            content_type='application/pdf',
                            as_attachment=True,
                            filename='%s %s %s.pdf' % (context['site_name'], _('Roster'), context['year']))
