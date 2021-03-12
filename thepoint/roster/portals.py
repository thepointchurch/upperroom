from datetime import date, timedelta

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..members.portals import Portal, PortalOperation
from .models import Role


class Details(Portal):
    order = -5
    title = _("Roster")
    template_name = "roster/portal_details.html"

    def get_context(self):
        context = super().get_context()
        try:
            context["role_list"] = (
                Role.current_objects.filter(people__id=self.request.user.person.id)
                .filter(meeting__date__lte=(date.today() + timedelta(days=60)))
                .select_related("meeting", "role", "location",)
                .prefetch_related("people", "people__family",)
                .only(
                    "description",
                    "meeting__date",
                    "role__name",
                    "location__name",
                    "people__name",
                    "people__suffix",
                    "people__surname_override",
                    "people__family__name",
                )
            )
        except Exception:  # pylint: disable=broad-except
            context["role_list"] = []
        context["person"] = getattr(self.request.user, "person", None)
        return context

    def will_show(self):
        return self.request.user.is_active and getattr(self.request.user, "person", None)


class BuilderOperation(PortalOperation):
    title = _("Roster Builder")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("roster:builder")
        return context

    def will_show(self):
        return self.request.user.is_active and self.request.user.has_perm("roster.add_meeting")


class RosterHomeOperation(PortalOperation):
    title = _("Meeting Roster")
    description = _("Roster for regular meetings.")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("roster:index")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )
