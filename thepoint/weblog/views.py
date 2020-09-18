from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from ..resources.views import RedirectToAttachment
from ..utils.mixin import NeverCacheMixin, VaryOnCookieMixin
from ..utils.storages.attachment import attachment_response
from .models import Attachment, WeblogEntry


class WeblogList(VaryOnCookieMixin, LoginRequiredMixin, generic.ListView):  # pylint: disable=too-many-ancestors
    template_name = "weblog/index.html"
    paginate_by = 10

    def get_queryset(self):
        return WeblogEntry.published_objects.all()


class WeblogDetail(VaryOnCookieMixin, LoginRequiredMixin, generic.DetailView):
    model = WeblogEntry
    template_name = "weblog/weblog_detail.html"

    def get_queryset(self):
        if self.request.user.is_staff:
            return WeblogEntry.objects.all()
        return WeblogEntry.published_objects.all()

    def get_object(self, **kwargs):  # pylint: disable=arguments-differ
        obj = super().get_object(**kwargs)
        if not obj.body and obj.alternates.count() == 1:
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
            filename=(attachment.clean_title + attachment.extension),
            content_type=attachment.mime_type,
        )
