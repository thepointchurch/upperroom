from django.urls import reverse

from ..members.portals import PortalOperation
from .models import Publication


class NewsletterHomeOperation(PortalOperation):
    slug = None

    @classmethod
    def get_instances(cls):
        return [
            type(cls.__class__.__name__, (cls,), {"title": p.name, "description": p.description, "slug": p.slug})
            for p in Publication.objects.all()
        ]

    def get_context(self):
        context = super().get_context()
        context["url"] = reverse(self.slug + ":index")
        return context

    def will_show(self):
        return (
            self.request.user.is_active
            and not self.request.user.is_staff
            and not getattr(self.request.user, "person", None)
        )
