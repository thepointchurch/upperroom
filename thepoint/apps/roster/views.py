# pylint: disable=too-many-ancestors

import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.forms import TextInput, models
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from weasyprint import HTML

from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from .forms import meetingbuilderformset_factory
from .models import Meeting, MeetingTemplate, Role, next_empty_meeting_date


class MeetingIndex(VaryOnCookieMixin, LoginRequiredMixin, generic.ListView):
    model = Meeting
    allow_future = True
    template_name = "roster/index.html"

    def get_queryset(self):
        return Meeting.current_objects.all()[:5]


class MonthlyMeetingView(VaryOnCookieMixin, LoginRequiredMixin, generic.MonthArchiveView):
    model = Meeting
    allow_future = True
    date_field = "date"
    make_object_list = True


class PublicPersonList(generic.ListView):
    model = Role
    template_name = "roster/person_list.html"

    def get_queryset(self):
        self.person = self.kwargs["pk"]  # pylint: disable=attribute-defined-outside-init
        return Role.current_objects.filter(people__id=self.person)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ..directory.models import Person  # pylint: disable=import-outside-toplevel

        context["person"] = Person.objects.get(id=self.person)
        return context


class PersonList(VaryOnCookieMixin, LoginRequiredMixin, PublicPersonList):
    pass


class PersonTaskList(NeverCacheMixin, PublicPersonList):
    template_name = "roster/person_task.ics"
    content_type = "text/calendar"


class PersonEventList(NeverCacheMixin, PublicPersonList):
    template_name = "roster/person_event.ics"
    content_type = "text/calendar"


class RosterPdf(NeverCacheMixin, PermissionRequiredMixin, generic.TemplateView):
    permission_required = ("roster.add_meeting",)
    template_name = "roster/pdf.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year")
        week_day = self.kwargs.get("week_day", 1)  # Sunday

        context = super().get_context_data(**kwargs)
        context["site_name"] = get_current_site(None).name
        context["contact_email"] = settings.ROSTER_EMAIL
        context["year"] = year
        context["meeting_list"] = Meeting.objects.all().filter(date__year=year, date__week_day=week_day)
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return FileResponse(
            io.BytesIO(HTML(string=response.render().content, encoding="utf-8").write_pdf()),
            content_type="application/pdf",
            as_attachment=True,
            filename="%s %s %s.pdf" % (context["site_name"], _("Roster"), context["year"]),
        )


class BuilderView(NeverCacheMixin, PermissionRequiredMixin, generic.edit.CreateView):
    model = Meeting
    permission_required = ("roster.add_meeting", "roster.add_role")
    template_name = "roster/builder.html"
    fields = ["date"]

    def get_context_data(self, **kwargs):
        if self.request.GET and "template" in self.request.GET:
            self.builder_template = get_object_or_404(  # NOQA: E501 pylint: disable=attribute-defined-outside-init
                MeetingTemplate, id=self.request.GET.get("template")
            )
        else:
            self.builder_template = MeetingTemplate.objects.order_by(  # NOQA: E501 pylint: disable=attribute-defined-outside-init
                "-is_default", "name"
            ).first()
        if self.request.GET and "by_name" in self.request.GET:
            sort_by_age = False
        else:
            sort_by_age = True

        data = super().get_context_data(**kwargs)

        if self.request.POST:
            data["roles"] = meetingbuilderformset_factory()(self.request.POST)
        else:
            data["builder_templates"] = MeetingTemplate.objects.all()
            data["sort_by_age"] = sort_by_age
            if self.builder_template:
                data["roles"] = meetingbuilderformset_factory(self.builder_template.roles.count())(
                    initial=[{"role": r} for r in self.builder_template.roles.all()],
                    form_kwargs={"sort_by_age": sort_by_age},
                )
                data["builder_template"] = self.builder_template

        return data

    def get_form_class(self):
        return models.modelform_factory(
            self.model, fields=self.fields, widgets={"date": TextInput(attrs={"title": "YYYY-MM-DD"})}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["label_suffix"] = ""
        return kwargs

    def get_initial(self):
        try:
            return {"date": next_empty_meeting_date(self.builder_template.week_day)}
        except AttributeError:
            return {}

    def get_success_url(self):
        return "%s?template=%d" % (reverse("roster:builder"), self.builder_template.id)

    def form_valid(self, form):
        context = self.get_context_data()
        roles = context["roles"]
        with transaction.atomic():
            obj = form.save()
            if roles.is_valid():
                roles.instance = obj
                roles.save()
        messages.success(
            self.request, _("Added %s meeting on %s") % (self.builder_template.name, obj.date.strftime("%A %-d %B %Y"))
        )
        return super().form_valid(form)
