# pylint: disable=too-many-ancestors

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from .models import Book


class IndexView(VaryOnCookieMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = "library/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = _("Library")
        return context


class SearchView(NeverCacheMixin, LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = "library/book_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metadata_description"] = None
        context["metadata_title"] = f"{_('Library')}: {self.request.GET.get('query', '')}"
        return context

    def get_queryset(self):  # pylint: disable=too-many-return-statements
        search_field = self.request.GET.get("field", "")
        search_query = self.request.GET.get("query", "")

        q_title = Q(title__icontains=search_query)
        q_subtitle = Q(subtitle__icontains=search_query)
        q_description = Q(description__icontains=search_query)
        q_type = Q(type__icontains=search_query)
        q_author = Q(author__icontains=search_query)
        q_isbn = Q(isbn__icontains=search_query)
        q_location = Q(location__icontains=search_query)

        if search_field == "title":
            return Book.objects.filter(q_title).distinct()
        if search_field == "subtitle":
            return Book.objects.filter(q_subtitle).distinct()
        if search_field == "description":
            return Book.objects.filter(q_description).distinct()
        if search_field == "type":
            return Book.objects.filter(q_type).distinct()
        if search_field == "author":
            return Book.objects.filter(q_author).distinct()
        if search_field == "isbn":
            return Book.objects.filter(q_isbn).distinct()
        if search_field == "location":
            return Book.objects.filter(q_location).distinct()
        return Book.objects.filter(
            q_title | q_subtitle | q_description | q_type | q_author | q_isbn | q_location
        ).distinct()
