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
    queryset = Family.active_objects.select_related(None).prefetch_related(None).only("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["directory_email"] = settings.DIRECTORY_EMAIL
        context["search_query"] = ""
        context["metadata_description"] = None
        context["metadata_title"] = _("Directory")
        context["has_archived"] = Family.archived_objects.exists()
        return context


class LetterView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    model = Family
    template_name = "directory/family_letter.html"
    permission_required = "directory.can_view"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["letter"] = self.kwargs["letter"]
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Directory')}: {self.kwargs['letter'].upper()}"
        return context

    def get_queryset(self):
        return Family.active_objects.filter(name__istartswith=self.kwargs["letter"])


class ArchivedView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    model = Family
    template_name = "directory/family_archived.html"
    permission_required = "directory.can_view"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Directory')}: Archived"
        return context

    def get_queryset(self):
        return Family.archived_objects.all()


class DetailView(VaryOnCookieMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Directory')}: {self.object.name}"
        return context

    def get_queryset(self):
        return Family.current_objects.all()


class SearchView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    model = Family
    template_name = "directory/family_search.html"
    permission_required = "directory.can_view"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_type"] = self.request.GET.get("type", _("By Name"))
        context["search_query"] = self.request.GET.get("query", "")
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Directory Search')}: {context['search_query']}"
        return context

    def get_queryset(self):
        search_type = self.request.GET.get("type", _("By Name"))
        search_query = self.request.GET.get("query", "")

        if search_query == "":
            return Family.current_objects.none()
        if search_type == _("By Location"):
            return Family.current_objects.filter(
                Q(street__icontains=search_query)
                | Q(suburb__icontains=search_query)
                | Q(postcode__icontains=search_query)
            ).distinct()
        search = Q()
        for part in search_query.split():
            search |= (
                (Q(members__name__icontains=part) | Q(members__surname_override__icontains=part))
                & Q(members__is_current=True)
            ) | Q(name__icontains=part)
        return Family.current_objects.filter(search).distinct()


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
            raise Http404(f"No family for the current user ({self.request.user}).") from exc
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PersonInlineFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = PersonInlineFormSet(instance=self.object)
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Directory Edit')}: {self.object.name}"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            self.object = form.save()  # pylint: disable=attribute-defined-outside-init
            formset.instance = self.object
            formset.save()
            family_updated.send(sender=self.object.__class__, instance=self.object, actor=self.request.user)
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(form=form))


class BirthdayView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    template_name = "directory/birthday_list.html"
    permission_required = "directory.can_view"
    queryset = Person.current_objects.exclude(birthday__isnull=True).only(
        "name", "suffix", "surname_override", "family__name", "birthday"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = _("Birthdays")
        return context


class AnniversaryView(VaryOnCookieMixin, PermissionRequiredMixin, generic.ListView):
    template_name = "directory/anniversary_list.html"
    permission_required = "directory.can_view"
    queryset = (
        Family.current_objects.filter(anniversary__isnull=False)
        .filter(husband__isnull=False, husband__is_current=True)
        .filter(wife__isnull=False, wife__is_current=True)
        .prefetch_related(None)
        .only(
            "name",
            "husband__name",
            "husband__suffix",
            "husband__surname_override",
            "wife__name",
            "wife__suffix",
            "wife__surname_override",
            "anniversary",
        )
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = _("Anniversaries")
        return context


class FamilyPhotoView(NeverCacheMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"

    def get(self, request, *args, **kwargs):
        family = self.get_object()
        return attachment_response(family.photo.file, False, content_type="image/jpeg")

    def get_queryset(self):
        return Family.current_objects.select_related(None).prefetch_related(None).only("id")


class FamilyThumbnailView(NeverCacheMixin, PermissionRequiredMixin, generic.DetailView):
    model = Family
    permission_required = "directory.can_view"

    def get(self, request, *args, **kwargs):
        family = self.get_object()
        return attachment_response(family.photo_thumbnail.file, False, content_type="image/jpeg")

    def get_queryset(self):
        return Family.current_objects.select_related(None).prefetch_related(None).only("id")


class PersonVcardList(PermissionRequiredMixin, generic.ListView):
    model = Person
    permission_required = "directory.can_view"
    template_name = "directory/vcard.vcf"
    content_type = "text/vcard"
    queryset = Person.current_objects.only(
        "name", "suffix", "surname_override", "family__name", "email", "family__email"
    )


class PdfView(NeverCacheMixin, PermissionRequiredMixin, generic.View):
    permission_required = "directory.can_view"
    FILE_NAME = "directory/directory.pdf"

    def get(self, request, *args, **kwargs):
        title = _("%(site)s Directory") % {"site": get_current_site(request).name}
        return attachment_response(self.FILE_NAME, filename=(f"{title}.pdf"), content_type="application/pdf")


class PdfViewCompact(PdfView):
    FILE_NAME = "directory/directory_compact.pdf"


class PrintView(NeverCacheMixin, PermissionRequiredMixin, generic.TemplateView):
    permission_required = "directory.add_family"
    template_name = "directory/print.html"

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
        context["families"] = Family.active_objects.all()
        context["archived_families"] = Family.archived_objects.all()
        context["birthdays"] = Person.current_objects.exclude(birthday__isnull=True).only(
            "name", "suffix", "surname_override", "family__name", "birthday"
        )
        context["anniversaries"] = (
            Family.current_objects.filter(anniversary__isnull=False)
            .filter(husband__isnull=False)
            .filter(wife__isnull=False)
            .prefetch_related(None)
            .only(
                "name",
                "husband__name",
                "husband__suffix",
                "husband__surname_override",
                "wife__name",
                "wife__suffix",
                "wife__surname_override",
                "anniversary",
            )
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        return FileResponse(
            io.BytesIO(HTML(string=response.render().content, encoding="utf-8").write_pdf()),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{context['site_name']} {_('Directory')} {context['year']}.pdf",
        )


class PrintViewCompact(PrintView):
    template_name = "directory/print_compact.html"

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
        context["families"] = Family.active_objects.all()
        context["archived_families"] = Family.archived_objects.all()
        return context
