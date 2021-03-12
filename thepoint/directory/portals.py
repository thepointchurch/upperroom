from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..members.portals import Portal, PortalOperation


class Search(Portal):
    order = 11
    title = _("Directory Search")
    template_name = "directory/portal_search.html"

    def get_context(self):
        context = super().get_context()
        context["search_query"] = ""
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)


class Details(Portal):
    order = 10
    title = _("Personal Data")
    template_name = "directory/portal_details.html"

    def get_context(self):
        context = super().get_context()
        context["person"] = getattr(self.request.user, "person", None)
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)


class EditOperation(PortalOperation):
    title = _("Edit Your Directory Entry")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("directory:detail", kwargs={"pk": self.request.user.person.family.id})
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)
