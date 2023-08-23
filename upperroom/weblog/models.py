import logging
import uuid

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..search.managers import SearchManager
from ..utils.func import IsNotEmpty
from ..utils.media import get_mime_anchor, is_video_embed
from ..utils.mime import guess_extension

logger = logging.getLogger(__name__)


class PublishedManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True).exclude(published__gt=timezone.now())


class WeblogSearchManager(SearchManager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_published=True)
            .exclude(published__gt=timezone.now())
            .prefetch_related(
                models.Prefetch("attachments", queryset=Attachment.alternates.order_by(), to_attr="alternates"),
            )
            .only("title", "slug", "description", "created")
            .annotate(has_body=IsNotEmpty("body"))
        )

    def get_custom_filter(self, request=None):
        parent_filter = super().get_custom_filter(request)
        if request is not None and request.user.is_authenticated:
            return parent_filter
        return parent_filter & models.Q(id__in=[])


class WeblogEntry(models.Model):
    title = models.CharField(max_length=64, verbose_name=_("title"))
    slug = models.SlugField(unique_for_month="created", verbose_name=_("slug"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    body = models.TextField(null=True, blank=True, verbose_name=_("body"))

    author = models.ForeignKey(
        "directory.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="weblogs",
        verbose_name=_("author"),
    )
    show_author = models.BooleanField(default=True, verbose_name=_("show author"))

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("modified"))
    published = models.DateTimeField(null=True, blank=True, verbose_name=_("published"))
    show_date = models.BooleanField(default=True, verbose_name=_("show date"))

    is_published = models.BooleanField(default=False, verbose_name=_("published"))

    objects = models.Manager()
    published_objects = PublishedManager()
    search_objects = WeblogSearchManager(title="icontains", description="icontains", body="icontains")

    class Meta:
        ordering = ["-published"]
        get_latest_by = "published"
        indexes = [
            models.Index(fields=["published"]),
            models.Index(fields=["is_published"]),
        ]
        verbose_name = _("weblog entry")
        verbose_name_plural = _("weblog entries")

    def __str__(self):
        return self.title

    @cached_property
    def alternates(self):
        return self.attachments.filter(kind=Attachment.KIND_ALTERNATE)

    @cached_property
    def anchor(self):
        if is_video_embed(self.body):
            return _("watch")
        return _("read")

    @cached_property
    def inlines(self):
        return self.attachments.filter(kind=Attachment.KIND_INLINE)

    @cached_property
    def description_attach(self):
        content = self.description
        content += "\n"
        for attachment in self.attachments.all():
            content += "\n" + attachment.markdown_link()
        return content

    @cached_property
    def body_attach(self):
        content = self.body
        content += "\n"
        for attachment in self.attachments.all():
            content += "\n" + attachment.markdown_link()
        return content

    def clean(self):
        if self.is_published and not self.published:
            self.published = self.modified or timezone.now()

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "weblog:detail", kwargs={"slug": self.slug, "year": self.created.year, "month": self.created.month}
        )


def get_attachment_filename(instance, filename):  # pylint: disable=unused-argument
    instance_uuid = str(instance.id)
    return "weblog/attachment/" + "/".join([instance_uuid[i : i + 2] for i in range(0, 8, 2)] + [instance_uuid])


class AttachmentAlternateManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(kind=Attachment.KIND_ALTERNATE)


class AttachmentInlineManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(kind=Attachment.KIND_INLINE)


class Attachment(models.Model):
    KIND_ALTERNATE = "A"
    KIND_INLINE = "I"
    KIND_CHOICES = (
        (KIND_ALTERNATE, _("Alternate")),
        (KIND_INLINE, _("Inline")),
    )

    _utf_translate = str.maketrans("\u2013\u201c\u201d", '-""')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, verbose_name="ID")

    title = models.CharField(max_length=64, verbose_name=_("title"))
    slug = models.SlugField(db_index=True, verbose_name=_("slug"))
    file = models.FileField(upload_to=get_attachment_filename, verbose_name=_("file"))
    mime_type = models.CharField(max_length=128, editable=False, verbose_name=_("MIME type"))
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, default=KIND_INLINE, verbose_name=_("kind"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    entry = models.ForeignKey(
        WeblogEntry,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("entry"),
    )

    objects = models.Manager()
    alternates = AttachmentAlternateManager()
    inlines = AttachmentInlineManager()

    class Meta:
        ordering = ["entry"]
        unique_together = ("entry", "slug")
        indexes = [
            models.Index(fields=["entry_id", "kind"]),
        ]
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return self.title

    @cached_property
    def anchor(self):
        anchor = get_mime_anchor(self.mime_type)
        if anchor:
            return _(anchor)
        return self.format

    @cached_property
    def clean_title(self):
        return self.title.translate(Attachment._utf_translate)

    @cached_property
    def extension(self):
        return guess_extension(self.mime_type)

    @cached_property
    def format(self):
        if self.extension:
            return self.extension.lstrip(".").upper()
        return "Unknown"

    def markdown_link(self):
        if self.description:
            description = f' "{self.description}"'
        else:
            description = ""
        return f"[{self.slug}]: {reverse('weblog:attachment', kwargs={'pk': self.id})}{description}"
