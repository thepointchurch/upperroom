from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from resources.models import Attachment, Resource, Tag


class TagList(generic.ListView):
    template_name = 'resources/tag.html'

    def get_queryset(self):
        self.tag = get_object_or_404(
            Tag, slug=self.kwargs.get('slug', None))

        if self.request.user.is_authenticated():
            resources = self.tag.resources.filter(is_published=True)
        else:
            resources = self.tag.resources.filter(is_published=True,
                                                  is_private=False)

        if self.tag.reverse_order:
            return resources.reverse()
        else:
            return resources

    def get_paginate_by(self, queryset):
        return self.tag.resources_per_page

    def get_context_data(self, **kwargs):
        context = super(TagList, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class ResourceList(generic.ListView):
    template_name = 'resources/index.html'
    paginate_by = 10

    def get_queryset(self):
        resources = Resource.published_objects\
            .filter(parent__isnull=True)\
            .exclude(tags__is_exclusive=True)
        if not self.request.user.is_authenticated():
            resources = resources.filter(is_private=False)
        return resources


class PermissionRequired(Exception):
    pass


class RedirectToAttachment(Exception):
    def __init__(self, attachment):
        super(RedirectToAttachment, self).__init__(str(attachment))
        self.attachment = attachment


class ResourceDetail(generic.DetailView):
    model = Resource

    def get_queryset(self):
        return Resource.published_objects.all()

    def get_object(self, **kwargs):
        obj = super(ResourceDetail, self).get_object(**kwargs)
        if obj.is_private and not self.request.user.is_authenticated():
            raise PermissionRequired('Resource is private')
        if not obj.body and obj.attachments.count() == 1:
            raise RedirectToAttachment(obj.attachments.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super(ResourceDetail, self).dispatch(*args, **kwargs)
        except PermissionRequired:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.path)
        except RedirectToAttachment as e:
            return redirect('resources:attachment', pk=e.attachment.id)


class AttachmentView(generic.DetailView):
    model = Attachment

    def get_object(self, **kwargs):
        obj = super(AttachmentView, self).get_object(**kwargs)
        if obj.is_private and not self.request.user.is_authenticated():
            raise PermissionRequired('Resource is private')
        return obj

    def get(self, request, *args, **kwargs):
        try:
            attachment = self.get_object()
        except PermissionRequired:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.path)

        if getattr(default_storage, 'offload', False):
            disposition = 'attachment; filename="%s%s"' % \
                (attachment.clean_title, attachment.extension)
            response_headers = {
                'response-content-disposition': disposition,
                'response-content-type':        attachment.mime_type,
            }
            response = HttpResponseRedirect(
                default_storage.url(attachment.file.name,
                                    response_headers=response_headers))
        else:
            response = HttpResponse(attachment.file,
                                    content_type=attachment.mime_type)
            response['Content-Disposition'] = ('attachment; filename="%s%s"' %
                                               (attachment.clean_title,
                                                attachment.extension))
        return response
