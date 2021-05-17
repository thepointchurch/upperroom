from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.views import generic

from ..resources.views import RedirectToAttachment
from ..utils.func import IsNotEmpty
from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .models import Attachment, WeblogEntry


class WeblogList(VaryOnCookieMixin, LoginRequiredMixin, generic.ListView):  # pylint: disable=too-many-ancestors
    template_name = "weblog/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            WeblogEntry.published_objects.select_related("author__family")
            .prefetch_related(
                Prefetch(
                    "attachments",
                    queryset=Attachment.alternates.only("id", "entry_id", "slug", "description", "mime_type"),
                    to_attr="alternates",
                ),
                Prefetch(
                    "attachments",
                    queryset=Attachment.inlines.only("id", "entry_id", "slug", "description"),
                    to_attr="inlines",
                ),
            )
            .only(
                "title",
                "slug",
                "description",
                "show_author",
                "created",
                "published",
                "modified",
                "show_date",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
            .annotate(has_body=IsNotEmpty("body"))
        )


class WeblogDetail(VaryOnCookieMixin, LoginRequiredMixin, generic.DetailView):
    model = WeblogEntry
    template_name = "weblog/weblog_detail.html"

    def get_queryset(self):
        if self.request.user.is_staff:
            manager = WeblogEntry.objects
        else:
            manager = WeblogEntry.published_objects
        return (
            manager.select_related("author__family")
            .prefetch_related(
                Prefetch(
                    "attachments",
                    queryset=Attachment.alternates.only("id", "entry_id", "slug", "description", "mime_type"),
                    to_attr="alternates",
                ),
                Prefetch(
                    "attachments",
                    queryset=Attachment.inlines.only("id", "entry_id", "slug", "description"),
                    to_attr="inlines",
                ),
            )
            .only(
                "title",
                "description",
                "body",
                "show_author",
                "is_published",
                "published",
                "modified",
                "show_date",
                "author__name",
                "author__suffix",
                "author__surname_override",
                "author__family__name",
            )
        )

    def get_object(self, **kwargs):  # pylint: disable=arguments-differ
        obj = super().get_object(**kwargs)
        try:
            count = obj.alternates.count()
        except TypeError:
            count = len(obj.alternates)
        if not obj.body and count == 1:
            raise RedirectToAttachment(obj.alternates.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super().dispatch(*args, **kwargs)
        except RedirectToAttachment as exc:
            return redirect("weblog:attachment", pk=exc.attachment.id)


class AttachmentView(NeverCacheMixin, LoginRequiredMixin, generic.DetailView):
    model = Attachment

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(
            attachment.file,
            filename=(attachment.clean_title + (attachment.extension or "")),
            content_type=attachment.mime_type,
        )

    def get_queryset(self):
        return Attachment.objects.only("id")
