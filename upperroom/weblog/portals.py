from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..members.portals import Portal, PortalOperation
from .models import WeblogEntry


class Latest(Portal):
    order = -8
    title = _("Weblog Entries")
    template_name = "weblog/portal_latest.html"

    def get_context(self):
        context = super().get_context()
        context["items"] = WeblogEntry.published_objects.only("title", "slug", "created")[:5]
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)


class WeblogHomeOperation(PortalOperation):
    title = _("Weblog")
    description = _("Check the latest weblog entries.")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("weblog:index")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )
