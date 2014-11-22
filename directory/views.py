from django.views import generic
from django.db.models import Q

from directory.models import Family, Person

class IndexView(generic.ListView):
    template_name = 'directory/index.html'
    queryset = Family.current_objects.all()

class LetterView(generic.ListView):
    model = Family
    template_name = 'directory/family_letter.html'

    def get_queryset(self):
        self.letter = self.kwargs['letter']
        return Family.current_objects.filter(name__startswith=self.letter)

class DetailView(generic.DetailView):
    model = Family

class SearchView(generic.ListView):
    model = Family
    template_name = 'directory/family_search.html'

    def get_queryset(self):
        self.search_type = self.request.GET.get('type', 'By Name')
        self.search_query = self.request.GET.get('query', '')

        if self.search_type == 'By Location':
            return Family.current_objects.filter(Q(street__icontains=self.search_query) | Q(suburb__icontains=self.search_query) | Q(postcode__icontains=self.search_query)).distinct()
        else:
            return Family.current_objects.filter(Q(name__icontains=self.search_query) | Q(members__name__icontains=self.search_query)).distinct()

class BirthdayView(generic.ListView):
    template_name = 'directory/birthday_list.html'
    queryset = Person.current_objects.all().exclude(birthday__isnull=True)

class AnniversaryView(generic.ListView):
    template_name = 'directory/anniversary_list.html'
    queryset = Family.current_objects.filter(husband__isnull=False).filter(husband__isnull=False)
