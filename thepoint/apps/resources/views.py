# pylint: disable=too-many-ancestors

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic

from ..directory.models import Person
from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .models import Attachment, Resource, ResourceFeed, Tag


class TagList(VaryOnCookieMixin, generic.ListView):
    template_name = "resources/tag.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            self.tag = get_object_or_404(  # pylint: disable=attribute-defined-outside-init
                Tag, slug=self.kwargs.get("slug", None)
            )
        else:
            self.tag = get_object_or_404(  # pylint: disable=attribute-defined-outside-init
                Tag.objects.filter(is_private=False), slug=self.kwargs.get("slug", None)
            )

        resources = self.tag.resources.filter(is_published=True, parent__isnull=True).exclude(
            published__gt=timezone.now()
        )
        if not self.request.user.is_authenticated:
            resources = resources.filter(is_private=False)

        if self.tag.reverse_order:
            return resources.reverse()
        return resources

    def get_paginate_by(self, queryset):
        return self.tag.resources_per_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class ResourceList(VaryOnCookieMixin, generic.ListView):
    template_name = "resources/index.html"
    paginate_by = 10

    def get_queryset(self):
        resources = Resource.published_objects.filter(parent__isnull=True).exclude(tags__is_exclusive=True)
        if not self.request.user.is_authenticated:
            resources = resources.filter(is_private=False)
        return resources

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = None
        return context


class RedirectToAttachment(Exception):
    def __init__(self, attachment):
        super().__init__(str(attachment))
        self.attachment = attachment


class ResourcePermissionMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        if isinstance(obj, Attachment):
            return self.request.user.is_authenticated or not obj.is_private
        return self.request.user.is_authenticated or (
            not obj.is_private and any(not t.is_private for t in obj.tags.all())
        )


class ResourceDetail(VaryOnCookieMixin, ResourcePermissionMixin, generic.DetailView):
    model = Resource

    def get_queryset(self):
        if self.request.user.is_staff:
            return Resource.objects.all()
        return Resource.published_objects.all()

    def get_object(self, **kwargs):  # pylint: disable=arguments-differ
        obj = super().get_object(**kwargs)
        if not obj.body and obj.attachments.count() == 1:
            raise RedirectToAttachment(obj.attachments.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super().dispatch(*args, **kwargs)
        except RedirectToAttachment as exc:
            return redirect("resources:attachment", pk=exc.attachment.id)


class AttachmentView(NeverCacheMixin, ResourcePermissionMixin, generic.DetailView):
    model = Attachment

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(
            attachment.file,
            filename=(attachment.clean_title + attachment.extension),
            content_type=attachment.mime_type,
        )


class AuthorList(VaryOnCookieMixin, generic.ListView):
    template_name = "resources/author.html"
    paginate_by = 10
    ordering = ["-published"]

    def get_queryset(self):
        author = get_object_or_404(Person, id=self.kwargs.get("pk", None))

        if self.request.user.is_authenticated:
            return author.resources.filter(is_published=True, show_author=True)
        return author.resources.filter(is_published=True, show_author=True, is_private=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = get_object_or_404(Person, id=self.kwargs.get("pk", None))
        context["tag"] = None
        return context


class FeedArtworkView(NeverCacheMixin, generic.DetailView):
    model = ResourceFeed

    def get(self, request, *args, **kwargs):
        feed = self.get_object()
        if not feed.artwork:
            raise Http404("This feed has no artwork")
        return attachment_response(feed.artwork, as_attachment=False)
