from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic

from directory.forms import FamilyForm, PersonForm, PersonInlineFormSet
from directory.models import Family, Person


class PrivateMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PrivateMixin, self).dispatch(*args, **kwargs)


class IndexView(PrivateMixin, generic.ListView):
    template_name = 'directory/index.html'
    queryset = Family.current_objects.all()


class LetterView(PrivateMixin, generic.ListView):
    model = Family
    template_name = 'directory/family_letter.html'

    def get_queryset(self):
        self.letter = self.kwargs['letter']
        return Family.current_objects.filter(name__startswith=self.letter)


class DetailView(PrivateMixin, generic.DetailView):
    model = Family


class SearchView(PrivateMixin, generic.ListView):
    model = Family
    template_name = 'directory/family_search.html'

    def get_queryset(self):
        self.search_type = self.request.GET.get('type', 'By Name')
        self.search_query = self.request.GET.get('query', '')

        q = self.search_query
        if self.search_type == 'By Location':
            return Family.current_objects.filter(
                Q(street__icontains=q) |
                Q(suburb__icontains=q) |
                Q(postcode__icontains=q)).distinct()
        else:
            return Family.current_objects.filter(
                Q(name__icontains=q) |
                (Q(members__name__icontains=q) &
                 Q(members__is_current=True))
                ).distinct()


class FamilyEditView(generic.edit.UpdateView):
    model = Family
    form_class = FamilyForm

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_queryset(self):
        try:
            self.kwargs['pk'] = self.request.user.person.family.pk
        except ObjectDoesNotExist:
            raise Http404('No family for the current user (%s).' %
                          self.request.user)
        return super(FamilyEditView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(FamilyEditView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PersonInlineFormSet(self.request.POST,
                                                     instance=self.object)
        else:
            context['formset'] = PersonInlineFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class BirthdayView(PrivateMixin, generic.ListView):
    template_name = 'directory/birthday_list.html'
    queryset = Person.current_objects.all().exclude(birthday__isnull=True)


class AnniversaryView(PrivateMixin, generic.ListView):
    template_name = 'directory/anniversary_list.html'
    queryset = Family.current_objects.filter(anniversary__isnull=False)\
        .filter(husband__isnull=False).filter(wife__isnull=False)
