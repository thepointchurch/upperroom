from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..members.portals import Portal, PortalOperation


class LibraryHomeOperation(PortalOperation):
    title = _("Library")
    description = _("Search the church library.")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("library:index")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )


class Search(Portal):
    order = 11
    title = _("Library Search")
    template_name = "library/portal_search.html"

    def get_context(self):
        context = super().get_context()
        context["search_query"] = ""
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)
