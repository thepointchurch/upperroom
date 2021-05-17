# pylint: disable=too-many-ancestors

from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import generic

from ..directory.models import Person
from ..utils.func import IsNotEmpty
from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .models import Attachment, Resource, ResourceFeed, Tag


class TagList(VaryOnCookieMixin, generic.ListView):
    template_name = "resources/tag.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tag = None

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Tag.objects.all()
        else:
            queryset = Tag.objects.filter(is_private=False)
        self.tag = get_object_or_404(
            queryset.prefetch_related(
                Prefetch("feeds", queryset=ResourceFeed.objects.only("title", "slug", "is_podcast"))
            ).only("name", "description", "priority"),
            slug=self.kwargs.get("slug", None),
        )

        resources = (
            self.tag.resources.filter(is_published=True, parent__isnull=True)
            .exclude(published__gt=timezone.now())
            .select_related("author__family")
            .prefetch_related(
                Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates"),
                Prefetch("attachments", queryset=Attachment.inlines.order_by(), to_attr="inlines"),
            )
            .only(
                "title",
                "slug",
                "description",
                "show_author",
                "published",
                "show_date",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
            .annotate(has_body=IsNotEmpty("body"))
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
            resources = resources.filter(is_private=False).exclude(tags__is_private=True)
        return (
            resources.select_related("author__family")
            .prefetch_related(
                Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates"),
                Prefetch("attachments", queryset=Attachment.inlines.order_by(), to_attr="inlines"),
            )
            .only(
                "title",
                "slug",
                "description",
                "show_author",
                "published",
                "show_date",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
            .annotate(has_body=IsNotEmpty("body"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = None
        return context


class RedirectToAttachment(Exception):
    def __init__(self, attachment):
        super().__init__(str(attachment))
        self.attachment = attachment


class ResourceDetail(VaryOnCookieMixin, generic.DetailView):
    model = Resource

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Resource.objects
        elif self.request.user.is_authenticated:
            queryset = Resource.published_objects
        else:
            queryset = Resource.published_objects.filter(is_private=False)
        return (
            queryset.select_related("author__family")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=Resource.objects.prefetch_related(
                        Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates")
                    ),
                ),
                Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates"),
                Prefetch("attachments", queryset=Attachment.inlines.order_by(), to_attr="inlines"),
            )
            .only(
                "title",
                "body",
                "show_author",
                "is_published",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
        )

    def get_object(self, **kwargs):  # pylint: disable=arguments-differ
        obj = super().get_object(**kwargs)
        if not self.request.user.is_authenticated and any(x.is_private for x in obj.tags.all()):
            raise Http404("Access Denied")
        try:
            count = obj.alternates.count()
        except TypeError:
            count = len(obj.alternates)
        if not obj.body and count == 1:
            raise RedirectToAttachment(obj.attachments.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super().dispatch(*args, **kwargs)
        except RedirectToAttachment as exc:
            return redirect("resources:attachment", pk=exc.attachment.id)


class AttachmentView(NeverCacheMixin, generic.DetailView):
    model = Attachment

    def get_object(self, **kwargs):  # pylint: disable=arguments-differ
        obj = super().get_object(**kwargs)
        if not self.request.user.is_authenticated and (
            obj.resource.is_private or any(x.is_private for x in obj.resource.tags.only("is_private"))
        ):
            raise Http404("Access Denied")
        return obj

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(
            attachment.file,
            filename=(attachment.clean_title + (attachment.extension or "")),
            content_type=attachment.mime_type,
        )

    def get_queryset(self):
        return Attachment.objects.select_related("resource").only("id", "resource__is_private")


class EnclosureView(AttachmentView):
    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(
            attachment.file,
            filename=(attachment.clean_title + (attachment.extension or "")),
            content_type=attachment.mime_type,
            signed=False,
        )


class AuthorList(VaryOnCookieMixin, generic.ListView):
    template_name = "resources/author.html"
    paginate_by = 10
    ordering = ["-published"]

    def get_queryset(self):
        resources = (
            Resource.published_objects.filter(author__id=self.kwargs.get("pk", None))
            .select_related("author__family")
            .prefetch_related(
                Prefetch(
                    "children",
                    queryset=Resource.objects.prefetch_related(
                        Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates")
                    ),
                ),
                Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates"),
                Prefetch("attachments", queryset=Attachment.inlines.order_by(), to_attr="inlines"),
            )
            .only(
                "title",
                "slug",
                "description",
                "show_author",
                "published",
                "show_date",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
            .annotate(has_body=IsNotEmpty("body"))
        )

        if self.request.user.is_authenticated:
            return resources.filter(is_published=True, show_author=True)
        return resources.filter(is_published=True, show_author=True, is_private=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author"] = get_object_or_404(
            Person.objects.select_related("family").only("name", "suffix", "surname_override", "family__name"),
            id=self.kwargs.get("pk", None),
        )
        context["tag"] = None
        return context


class FeedArtworkView(NeverCacheMixin, generic.DetailView):
    model = ResourceFeed

    def get(self, request, *args, **kwargs):
        feed = self.get_object()
        if not feed.artwork:
            raise Http404("This feed has no artwork")
        return attachment_response(feed.artwork, as_attachment=False, signed=False)
