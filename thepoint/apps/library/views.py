from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views import generic

from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from .models import Book


class IndexView(VaryOnCookieMixin, LoginRequiredMixin, generic.TemplateView):
    template_name = 'library/index.html'


class SearchView(NeverCacheMixin, LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'library/book_list.html'

    def get_queryset(self):
        self.search_field = self.request.GET.get('field', '')
        self.search_query = self.request.GET.get('query', '')

        q_title = Q(title__icontains=self.search_query)
        q_subtitle = Q(subtitle__icontains=self.search_query)
        q_description = Q(description__icontains=self.search_query)
        q_type = Q(type__icontains=self.search_query)
        q_author = Q(author__icontains=self.search_query)
        q_isbn = Q(isbn__icontains=self.search_query)
        q_location = Q(location__icontains=self.search_query)

        if self.search_field == 'title':
            return Book.objects.filter(q_title).distinct()
        elif self.search_field == 'subtitle':
            return Book.objects.filter(q_subtitle).distinct()
        elif self.search_field == 'description':
            return Book.objects.filter(q_description).distinct()
        elif self.search_field == 'type':
            return Book.objects.filter(q_type).distinct()
        elif self.search_field == 'author':
            return Book.objects.filter(q_author).distinct()
        elif self.search_field == 'isbn':
            return Book.objects.filter(q_isbn).distinct()
        elif self.search_field == 'location':
            return Book.objects.filter(q_location).distinct()
        else:
            return Book.objects.filter(q_title |
                                       q_subtitle |
                                       q_description |
                                       q_type |
                                       q_author |
                                       q_isbn |
                                       q_location).distinct()
