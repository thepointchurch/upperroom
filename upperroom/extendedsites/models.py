from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _


class ExtendedSiteManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().prefetch_related("keywords")


class ExtendedSite(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        verbose_name=_("site"),
        related_name="extra",
        primary_key=True,
    )

    subtitle = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("subtitle"))

    description = models.CharField(max_length=256, null=True, blank=True, verbose_name=_("description"))

    objects = ExtendedSiteManager()

    class Meta:
        verbose_name = _("Extended Site")
        verbose_name_plural = _("Extended Sites")

    def __str__(self):
        return self.site.domain


class Keyword(models.Model):
    value = models.CharField(max_length=64, verbose_name=_("value"))
    order = models.SmallIntegerField(null=True, blank=True, verbose_name=_("order"))
    site = models.ForeignKey(ExtendedSite, on_delete=models.CASCADE, related_name="keywords", verbose_name=_("site"))

    class Meta:
        ordering = ["order", "value"]
        indexes = [
            models.Index(fields=["order", "value"]),
        ]
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")

    def __str__(self):
        return self.value
