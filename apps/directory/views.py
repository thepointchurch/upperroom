from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views import generic

from directory.forms import FamilyForm, PersonInlineFormSet
from directory.models import Family, Person
from directory.signals import family_updated


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'directory/index.html'
    queryset = Family.current_objects.all()


class LetterView(LoginRequiredMixin, generic.ListView):
    model = Family
    template_name = 'directory/family_letter.html'

    def get_queryset(self):
        self.letter = self.kwargs['letter']
        return Family.current_objects.filter(name__istartswith=self.letter)


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Family


class SearchView(LoginRequiredMixin, generic.ListView):
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


class FamilyEditView(LoginRequiredMixin, generic.edit.UpdateView):
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
            family_updated.send(sender=self.object.__class__, instance=self.object)
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class BirthdayView(LoginRequiredMixin, generic.ListView):
    template_name = 'directory/birthday_list.html'
    queryset = Person.current_objects.all().exclude(birthday__isnull=True)


class AnniversaryView(LoginRequiredMixin, generic.ListView):
    template_name = 'directory/anniversary_list.html'
    queryset = (Family.current_objects
                .filter(anniversary__isnull=False)
                .filter(husband__isnull=False)
                .filter(wife__isnull=False)
                )


class PdfView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        title = _('%(site)s Directory') % {'site': settings.SITE_NAME}
        if getattr(default_storage, 'offload', False):
            disposition = 'attachment; filename="%s.pdf"' % title
            response_headers = {
                'response-content-disposition': disposition,
                'response-content-type':        'application/pdf',
            }
            response = HttpResponseRedirect(
                default_storage.url('directory/directory.pdf',
                                    response_headers=response_headers))
        else:
            fsock = open('%s/directory/directory.pdf' % settings.MEDIA_ROOT, 'rb')
            response = HttpResponse(fsock, content_type='application/pdf')
            response['Content-Disposition'] = ('attachment; filename="%s.pdf"' % title)
        return response
