from datetime import date, timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import password_change as dist_password_change
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import generic

from directory.models import Person
from roster.models import Role

class IndexView(generic.TemplateView):
    template_name = 'members/index.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(IndexView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            context['role_list'] = Role.current_objects.filter(person__id=self.request.user.person.id).filter(meeting__date__lte=(date.today() + timedelta(days=60)))
        except: pass
        return context

def not_a_guest(user):
    try:
        return user.is_authenticated() and (user.is_staff or user.person)
    except:
        raise PermissionDenied

@user_passes_test(not_a_guest)
def password_change(request, *args, **kwargs):
    result = dist_password_change(request, *args, **kwargs)
    if result.__class__ == HttpResponseRedirect:
        messages.success(request, 'Your password has been changed successfully.')
    return result

class CreateView(generic.ListView):
    model = Person
    template_name = 'members/create_search.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.query = self.request.GET.get('query', '')

        if self.query == '':
            return Person.current_objects.none()
        else:
            return Person.current_objects.filter(user__isnull=True).filter(Q(name__icontains=self.query) | Q(family__name__icontains=self.query)).distinct()

class CreateConfirmView(generic.edit.CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'members/create_form.html'
    success_url = reverse_lazy('members:index')

    def get_context_data(self, **kwargs):
        context = super(CreateConfirmView, self).get_context_data(**kwargs)
        context['person'] = get_object_or_404(Person, pk=self.kwargs.get(self.pk_url_kwarg, None))
        return context

    def post(self, request, *args, **kwargs):
        person = get_object_or_404(Person, pk=self.kwargs.get(self.pk_url_kwarg, None))
        result = super(CreateConfirmView, self).post(request, *args, **kwargs)
        person.user = self.object
        person.save()

        # slight hack to log in as the new user
        logout(request)
        self.object.backend='django.contrib.auth.backends.ModelBackend'
        login(request, self.object)

        messages.success(request, 'Your account has been set up.')

        return result
