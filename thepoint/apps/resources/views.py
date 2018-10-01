from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from .models import Attachment, Resource, ResourceFeed, Tag
from ..utils.storages.attachment import attachment_response


class TagList(generic.ListView):
    template_name = 'resources/tag.html'

    def get_queryset(self):
        self.tag = get_object_or_404(
            Tag, slug=self.kwargs.get('slug', None))

        if self.request.user.is_authenticated:
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
        resources = (Resource.published_objects
                     .filter(parent__isnull=True)
                     .exclude(tags__is_exclusive=True)
                     )
        if not self.request.user.is_authenticated:
            resources = resources.filter(is_private=False)
        return resources


class RedirectToAttachment(Exception):
    def __init__(self, attachment):
        super(RedirectToAttachment, self).__init__(str(attachment))
        self.attachment = attachment


class ResourcePermissionMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return not obj.is_private or self.request.user.is_authenticated


class ResourceDetail(ResourcePermissionMixin, generic.DetailView):
    model = Resource

    def get_queryset(self):
        return Resource.published_objects.all()

    def get_object(self, **kwargs):
        obj = super(ResourceDetail, self).get_object(**kwargs)
        if not obj.body and obj.attachments.count() == 1:
            raise RedirectToAttachment(obj.attachments.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super(ResourceDetail, self).dispatch(*args, **kwargs)
        except RedirectToAttachment as e:
            return redirect('resources:attachment', pk=e.attachment.id)


class AttachmentView(ResourcePermissionMixin, generic.DetailView):
    model = Attachment

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(attachment.file,
                                   filename=(attachment.clean_title + attachment.extension),
                                   content_type=attachment.mime_type)


class FeedArtworkView(generic.DetailView):
    model = ResourceFeed

    def get(self, request, *args, **kwargs):
        feed = self.get_object()
        if not feed.artwork:
            raise Http404('This feed has no artwork')
        return attachment_response(feed.artwork, as_attachment=False)
