from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from .models import Attachment, WeblogEntry
from ..resources.views import RedirectToAttachment
from ..utils.storages.attachment import attachment_response


class WeblogList(LoginRequiredMixin, generic.ListView):
    template_name = 'weblog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return WeblogEntry.published_objects.all()


class WeblogDetail(LoginRequiredMixin, generic.DetailView):
    model = WeblogEntry
    template_name = 'weblog/weblog_detail.html'

    def get_queryset(self):
        return WeblogEntry.published_objects.all()

    def get_object(self, **kwargs):
        obj = super(WeblogDetail, self).get_object(**kwargs)
        if not obj.body and obj.alternates.count() == 1:
            raise RedirectToAttachment(obj.alternates.first())
        return obj

    def dispatch(self, *args, **kwargs):
        try:
            return super(WeblogDetail, self).dispatch(*args, **kwargs)
        except RedirectToAttachment as e:
            return redirect('weblog:attachment', pk=e.attachment.id)


class AttachmentView(LoginRequiredMixin, generic.DetailView):
    model = Attachment

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        return attachment_response(attachment.file,
                                   filename=(attachment.clean_title + attachment.extension),
                                   content_type=attachment.mime_type)
