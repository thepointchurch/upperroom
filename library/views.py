from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic

from library.models import Book


@login_required
def index(request):
    return render(request, 'library/index.html')


class PrivateMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PrivateMixin, self).dispatch(*args, **kwargs)


class SearchView(PrivateMixin, generic.ListView):
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
