from django.db import models
from django.utils.translation import gettext_lazy as _


class Splash(models.Model):
    POSITION_ABOVE = "A"
    POSITION_BELOW = "B"
    POSITION_CHOICES = (
        (POSITION_ABOVE, _("Above")),
        (POSITION_BELOW, _("Below")),
    )

    title = models.CharField(max_length=256, verbose_name=_("title"))
    content = models.TextField(null=True, blank=True, verbose_name=_("content"))
    order = models.SmallIntegerField(null=True, blank=True, verbose_name=_("order"))
    position = models.CharField(
        max_length=1,
        choices=POSITION_CHOICES,
        default=POSITION_ABOVE,
        verbose_name=_("position"),
    )
    url = models.CharField(max_length=100, default="/")
    is_current = models.BooleanField(default=True, verbose_name=_("current"))
    is_private = models.BooleanField(default=False, verbose_name=_("private"))

    class Meta:
        ordering = ["url", "position", "order", "title"]
        indexes = [
            models.Index(fields=["is_current", "position"]),
            models.Index(fields=["url", "position", "order", "title"]),
        ]
        verbose_name = _("splash")
        verbose_name_plural = _("splashes")

    def __str__(self):
        return self.title


def get_splashes(request, position):
    if request.user.is_authenticated:
        return (
            Splash.objects.filter(is_current=True, url=request.path, position=position)
            .order_by("order", "title")
            .only("title", "content")
        )
    return (
        Splash.objects.filter(is_current=True, url=request.path, position=position, is_private=False)
        .order_by("order", "title")
        .only("title", "content")
    )
