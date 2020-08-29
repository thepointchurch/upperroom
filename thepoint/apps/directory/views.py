# pylint: disable=too-many-ancestors

import io
import time

from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from django.utils.dates import MONTHS
from django.utils.translation import gettext as _
from django.views import generic
from weasyprint import HTML

from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .forms import FamilyForm, PersonInlineFormSet
from .models import Family, Person
from .signals import family_updated


class IndexView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    template_name = "directory/index.html"
    permission_required = "directory.can_view"
    queryset = Family.current_objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["directory_email"] = settings.DIRECTORY_EMAIL
        return context


class LetterView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    model = Family
    template_name = "directory/family_letter.html"
    permission_required = "directory.can_view"

    def get_queryset(self):
        letter = self.kwargs["letter"]
        return Family.current_objects.filter(name__istartswith=letter)


class DetailView(VaryOnCookieMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"


class SearchView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    model = Family
    template_name = "directory/family_search.html"
    permission_required = "directory.can_view"

    def get_queryset(self):
        search_type = self.request.GET.get("type", "By Name")
        search_query = self.request.GET.get("query", "")

        query = search_query
        if search_type == "By Location":
            return Family.current_objects.filter(
                Q(street__icontains=query) | Q(suburb__icontains=query) | Q(postcode__icontains=query)
            ).distinct()
        return Family.current_objects.filter(
            Q(name__icontains=query)
            | (
                (Q(members__name__icontains=query) | Q(members__surname_override__icontains=query))
                & Q(members__is_current=True)
            )
        ).distinct()


class FamilyEditView(NeverCacheMixin, PermissionRequiredMixin, generic.edit.UpdateView):
    model = Family
    form_class = FamilyForm
    permission_required = "directory.can_view"

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_queryset(self):
        try:
            self.kwargs["pk"] = self.request.user.person.family.pk
        except ObjectDoesNotExist as exc:
            raise Http404("No family for the current user (%s)." % self.request.user) from exc
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PersonInlineFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = PersonInlineFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()  # pylint: disable=attribute-defined-outside-init
            formset.instance = self.object
            formset.save()
            family_updated.send(sender=self.object.__class__, instance=self.object)
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class BirthdayView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    template_name = "directory/birthday_list.html"
    permission_required = "directory.can_view"
    queryset = Person.current_objects.all().exclude(birthday__isnull=True)


class AnniversaryView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    template_name = "directory/anniversary_list.html"
    permission_required = "directory.can_view"
    queryset = (
        Family.current_objects.filter(anniversary__isnull=False)
        .filter(husband__isnull=False)
        .filter(wife__isnull=False)
    )


class FamilyPhotoView(NeverCacheMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"

    def get(self, request, *args, **kwargs):
        family = self.get_object()
        return attachment_response(family.photo.file, False, content_type="image/jpeg")


class FamilyThumbnailView(NeverCacheMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"

    def get(self, request, *args, **kwargs):
        family = self.get_object()
        return attachment_response(family.photo_thumbnail.file, False, content_type="image/jpeg")


DIRECTORY_FILE_NAME = "directory/directory.pdf"


class PdfView(NeverCacheMixin, PermissionRequiredMixin, generic.View):
    permission_required = "directory.can_view"

    def get(self, request, *args, **kwargs):
        title = _("%(site)s Directory") % {"site": get_current_site(request).name}
        return attachment_response(DIRECTORY_FILE_NAME, filename=("%s.pdf" % title), content_type="application/pdf")


class PrintView(NeverCacheMixin, PermissionRequiredMixin, generic.TemplateView):
    permission_required = "directory.add_family"
    template_name = "directory/print.html"
    permission_required = "directory.can_view"

    def get_context_data(self, **kwargs):
        month = self.request.GET.get("month") or time.localtime().tm_mon
        month = MONTHS[month]
        year = self.request.GET.get("year") or time.localtime().tm_year
        year = int(year)

        context = super().get_context_data(**kwargs)
        context["site_name"] = get_current_site(None).name
        context["contact_email"] = settings.DIRECTORY_EMAIL
        context["month"] = month
        context["year"] = year
        context["families"] = Family.current_objects.all()
        context["birthdays"] = Person.current_objects.all().exclude(birthday__isnull=True)
        context["anniversaries"] = (
            Family.current_objects.filter(anniversary__isnull=False)
            .filter(husband__isnull=False)
            .filter(wife__isnull=False)
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return FileResponse(
            io.BytesIO(HTML(string=response.render().content, encoding="utf-8").write_pdf()),
            content_type="application/pdf",
            as_attachment=True,
            filename="%s %s %s.pdf" % (context["site_name"], _("Directory"), context["year"]),
        )
