import inspect

from django.apps import apps
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _


class PortalBase:
    order = 0
    title = None

    def __init__(self, request):
        self.request = request

    def __str__(self):
        raise NotImplementedError

    def get_context(self):
        return {
            "order": self.order,
            "title": self.title,
        }

    def will_show(self):  # pylint: disable=no-self-use
        return True

    @classmethod
    def get_instances(cls):
        return [cls]

    @classmethod
    def get_portals(cls):
        instances = {}
        for app in apps.get_app_configs():
            try:
                for class_name, portal in inspect.getmembers(
                    app.module.portals, lambda x: inspect.isclass(x) and issubclass(x, cls)
                ):
                    if portal == cls:
                        continue
                    for portal_instance in portal.get_instances():
                        instances[portal_instance.order, portal_instance.title or class_name] = portal_instance
            except AttributeError:
                continue
        return [instances[x] for x in sorted(instances.keys())]


class Portal(PortalBase):
    template_name = "members/portal.html"

    def __str__(self):
        if not self.will_show():
            return ""

        try:
            return render_to_string(self.template_name, self.get_context())
        except NoReverseMatch:
            return ""


class PortalOperation(PortalBase):
    description = None

    def __str__(self):
        if not self.will_show():
            return ""

        try:
            context = self.get_context()
            return '<li><a href="%s">%s</a>%s</li>' % (
                escape(context.get("url", "")),
                escape(context.get("title", self.title)),
                escape(context.get("description", "")),
            )
        except NoReverseMatch:
            return ""

    def get_context(self):
        context = super().get_context()
        if self.description:
            context["description"] = " " + str(self.description)
        return context


class Operations(Portal):
    order = -10
    title = _("Operations")
    template_name = "members/portal_ops.html"

    def get_context(self):
        context = super().get_context()
        context["operations"] = [operation(self.request) for operation in PortalOperation.get_portals()]
        return context

    def will_show(self):
        return self.request.user.is_active and (
            self.request.user.is_staff or getattr(self.request.user, "person", None)
        )


class HomePage(Portal):
    order = -10
    title = None
    template_name = "members/portal_home.html"

    def get_context(self):
        context = super().get_context()
        context["operations"] = [operation(self.request) for operation in PortalOperation.get_portals()]
        context["webmaster_email"] = settings.WEBMASTER_EMAIL
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )


class AdminOperation(PortalOperation):
    order = -10
    title = _("Admin Site")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("admin:index")
        return context

    def will_show(self):
        return self.request.user.is_active and self.request.user.is_staff


class PasswordOperation(PortalOperation):
    order = 10
    title = _("Change Your Password")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("members:password_change")
        return context

    def will_show(self):
        return self.request.user.is_active and (
            self.request.user.is_staff or getattr(self.request.user, "person", None)
        )


class TechDetailsOperation(PortalOperation):
    order = 9
    title = _("Tech Details")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("members:tech")
        return context

    def will_show(self):
        return self.request.user.is_active and self.request.user.is_staff


class CreateAccountOperation(PortalOperation):
    order = 10
    title = _("Create Account")
    description = _(
        "Create a personal account for access to member functions. "
        "Note, you must be a current member to create an account."
    )

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("members:create")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )


class CalendarHomeOperation(PortalOperation):
    title = _("Event Calendar")
    description = _("A calendar of church events.")

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse("calendar")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )
