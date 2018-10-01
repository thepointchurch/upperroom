import logging
from datetime import date, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ..directory.models import Person
from ..roster.models import Role


logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'members/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        try:
            context['role_list'] = (Role.current_objects
                                    .filter(people__id=self.request.user.person.id)
                                    .filter(meeting__date__lte=(date.today() +
                                                                timedelta(days=60)))
                                    )
        except:
            pass
        context['webmaster_email'] = settings.WEBMASTER_EMAIL
        return context


def not_a_guest(user):
    try:
        return user.is_authenticated and (user.is_staff or user.person)
    except:
        raise PermissionDenied


class CreateView(LoginRequiredMixin, generic.ListView):
    model = Person
    template_name = 'members/create_search.html'

    def get_queryset(self):
        self.query = self.request.GET.get('query', '')

        if self.query == '':
            return Person.current_objects.none()
        else:
            return Person.current_objects.filter(user__isnull=True).filter(
                Q(name__icontains=self.query) |
                Q(family__name__icontains=self.query)).distinct()


class CreateConfirmView(LoginRequiredMixin, generic.edit.CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'members/create_form.html'
    success_url = reverse_lazy('members:index')

    def get_context_data(self, **kwargs):
        context = super(CreateConfirmView, self).get_context_data(**kwargs)
        context['person'] = get_object_or_404(
            Person, pk=self.kwargs.get(self.pk_url_kwarg, None))
        return context

    def post(self, request, *args, **kwargs):
        person = get_object_or_404(
            Person, pk=self.kwargs.get(self.pk_url_kwarg, None))

        try:
            User.objects.get(username=request.POST['username'])
            messages.error(request, _('A user with that username already exists.'))
            return redirect(request.path)
        except User.DoesNotExist:
            pass

        if request.POST['password1'] != request.POST['password2']:
            messages.error(request, _("The two password fields didn't match."))
            return redirect(request.path)

        result = super(CreateConfirmView, self).post(request, *args, **kwargs)

        if not self.object:
            logger.error('Error creating user %r' % self.object)
            messages.error(request, _('An error occurred trying to create your account.'))
            return redirect(request.path)

        person.user = self.object
        person.save()

        # slight hack to log in as the new user
        logout(request)
        self.object.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, self.object)

        messages.success(request, _('Your account has been set up successfully.'))

        return result
