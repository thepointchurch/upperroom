from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views import generic

from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .models import Issue, Publication


class PublicationMixin(UserPassesTestMixin):
    def test_func(self):
        self.publication = get_object_or_404(
            Publication,
            slug=self.request.resolver_match.namespace)
        return (not self.publication.is_private or
                self.request.user.is_authenticated)


class IndexView(VaryOnCookieMixin, PublicationMixin, generic.ListView):
    template_name = 'newsletter/index.html'
    paginate_by = 10

    def get_queryset(self):
        return self.publication.issues.all()

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['publication'] = self.publication
        return context


class DetailView(NeverCacheMixin, PublicationMixin, generic.DetailView):
    model = Issue

    def get_queryset(self):
        return self.publication.issues.all()

    def get(self, request, *args, **kwargs):
        issue = self.get_object()
        return attachment_response(issue.file,
                                   filename='%s %s%s' % (issue.publication.name, issue.date, issue.extension),
                                   content_type=issue.mime_type)
