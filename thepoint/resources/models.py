import logging
from itertools import chain

import mutagen
from django.core.validators import RegexValidator
from django.db import models
from django.http import Http404
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..utils.storages.attachment import attachment_url

logger = logging.getLogger(__name__)


class FeaturedMixin(models.Model):
    priority = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text=_("A non-empty value will feature this item " "in the main menu."),
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["priority"]),
        ]

    @property
    def is_featured(self):
        return self.priority is not None


class FeaturedManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(priority__isnull=False)


class Tag(FeaturedMixin, models.Model):
    name = models.CharField(max_length=64, verbose_name=_("name"))
    slug = models.SlugField(unique=True, verbose_name=_("slug"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))

    resources_per_page = models.PositiveSmallIntegerField(
        default=10, null=True, blank=True, verbose_name=_("resources per page"),
    )
    reverse_order = models.BooleanField(default=False, verbose_name=_("reverse order"))
    show_date = models.BooleanField(default=True, verbose_name=_("show date"))

    # Items with an exclusive tag only appear when searching for this tag.
    is_exclusive = models.BooleanField(default=False, verbose_name=_("exclusive"))

    is_private = models.BooleanField(default=False, verbose_name=_("private"))

    objects = models.Manager()
    featured_objects = FeaturedManager()

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_exclusive"]),
            models.Index(fields=["is_private"]),
        ]
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name

    def get_absolute_url(self):
        # should we search for conflicting URLs?
        if self.is_featured:
            url = "/%s/" % self.slug
            try:
                resolve(url)
            except Http404:
                return url
        return reverse("resources:tag", kwargs={"slug": self.slug})


class PublishedManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True).exclude(published__gt=timezone.now())


class Resource(FeaturedMixin, models.Model):
    title = models.CharField(max_length=64, verbose_name=_("title"))
    slug = models.SlugField(unique=True, verbose_name=_("slug"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    body = models.TextField(null=True, blank=True, verbose_name=_("body"))

    tags = models.ManyToManyField(Tag, blank=True, related_name="resources", verbose_name=_("tags"))

    author = models.ForeignKey(
        "directory.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
        verbose_name=_("author"),
    )
    show_author = models.BooleanField(default=True, verbose_name=_("show author"))

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children", verbose_name=_("parent"),
    )

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("modified"))
    published = models.DateTimeField(null=True, blank=True, verbose_name=_("published"))
    show_date = models.BooleanField(default=True, verbose_name=_("show date"))

    is_published = models.BooleanField(default=False, verbose_name=_("published"))
    is_private = models.BooleanField(default=False, verbose_name=_("private"))

    objects = models.Manager()
    published_objects = PublishedManager()
    featured_objects = FeaturedManager()

    class Meta:
        ordering = ["-published"]
        get_latest_by = "published"
        indexes = [
            models.Index(fields=["published"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["is_private"]),
        ]
        verbose_name = _("resource")
        verbose_name_plural = _("resources")

    def __str__(self):
        return self.title

    @cached_property
    def alternates(self):
        return self.attachments.filter(kind=Attachment.KIND_ALTERNATE)

    @cached_property
    def inlines(self):
        return self.attachments.filter(kind=Attachment.KIND_INLINE)

    @cached_property
    def content(self):
        content = self.body
        content += "\n"
        for child in self.children.all():
            content += "\n%s" % child.markdown_link()
            for child_alt in child.alternates:
                content += "\n%s" % child_alt.markdown_link(slug=True)
        for attachment in self.inlines:
            content += "\n%s" % attachment.markdown_link()
        return content

    @cached_property
    def is_private_full(self):
        if self.is_private:
            return True
        return any(tag.is_private for tag in self.tags.all())

    def clean(self):
        if self.is_published and not self.published:
            self.published = self.modified or timezone.now()

    def get_absolute_url(self):
        # should we search for conflicting URLs?
        if self.is_featured:
            url = "/%s" % self.slug
            try:
                resolve(url)
            except Http404:
                return url
        return reverse("resources:detail", kwargs={"slug": self.slug})

    def markdown_link(self, slug=False):
        return "[%s]: %s" % (
            self.slug if slug else self.title,
            reverse("resources:detail", kwargs={"slug": self.slug}),
        )


def get_attachment_filename(instance, filename):
    try:
        extension = "." + filename.split(".")[-1]
    except IndexError:
        extension = ""
    return "resource/attachment/%s/%s%s" % (instance.resource.slug, instance.slug, extension)


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

    title = models.CharField(max_length=64, verbose_name=_("title"))
    slug = models.SlugField(db_index=True, verbose_name=_("slug"))
    file = models.FileField(upload_to=get_attachment_filename, verbose_name=_("file"))
    mime_type = models.CharField(max_length=128, editable=False, verbose_name=_("MIME type"))
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, default=KIND_INLINE, verbose_name=_("kind"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="attachments", verbose_name=_("resource"),
    )
    metadata = models.JSONField(null=True, blank=True, verbose_name=_("metadata"))

    objects = models.Manager()
    alternates = AttachmentAlternateManager()
    inlines = AttachmentInlineManager()

    class Meta:
        ordering = ["resource"]
        unique_together = ("resource", "slug")
        indexes = [
            models.Index(fields=["kind"]),
        ]
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    def __str__(self):
        return self.title

    @cached_property
    def clean_title(self):
        return self.title.translate(Attachment._utf_translate)

    @cached_property
    def extension(self):
        try:
            return "." + self.file.name.split(".")[-1]
        except IndexError:
            return None

    @cached_property
    def format(self):
        if self.extension:
            return self.extension.lstrip(".").upper()
        return "Unknown"

    @cached_property
    def is_podcast_audio(self):
        if self.mime_type.split("/")[0] != "audio":
            return False

        for tag in self.resource.tags.all():
            if tag.feeds.filter(is_podcast=True):
                return True

        return False

    @property
    def is_private(self):
        return self.resource.is_private_full

    @cached_property
    def size(self):
        return self.file.size

    def markdown_link(self, slug=False):
        if self.description:
            description = ' "%s"' % self.description
        else:
            description = ""
        return "[%s]: %s%s" % (
            self.slug if slug else self.title,
            reverse("resources:attachment", kwargs={"pk": self.id}),
            description,
        )

    def update_metadata(self):
        if self.mime_type.split("/")[0] == "audio":
            try:
                mg_file = mutagen.File(self.file)
                metadata = {"length": str(int(mg_file.info.length))}
                if mg_file.info.channels:
                    metadata["channels"] = str(mg_file.info.channels)
                if mg_file.info.bitrate:
                    metadata["bitrate"] = str(mg_file.info.bitrate)
                if mg_file.info.sample_rate:
                    metadata["sample_rate"] = str(mg_file.info.sample_rate)
                self.metadata = metadata

                if self.is_podcast_audio:
                    self.update_podcast_tags_mp3(mg_file)
            except mutagen.MutagenError:
                self.metadata = {}
        else:
            self.metadata = {}

    def update_podcast_tags_mp3(self, mediafile):
        if self.mime_type not in ["audio/mp3", "audio/mpeg"]:
            return

        feed = None
        for tag in self.resource.tags.all():
            feed = tag.feeds.filter(is_podcast=True).first()
            break

        if not feed:
            return

        id3_tags = [
            ("TALB", mutagen.id3.TALB, feed.title),
            ("TIT2", mutagen.id3.TIT2, self.resource.title),
            ("TCON", mutagen.id3.TCON, "Podcast"),
        ]
        if self.resource.published:
            id3_tags.append(("TDRC", mutagen.id3.TDRC, self.resource.published.strftime("%Y-%m-%d")))
        if self.resource.author:
            id3_tags.append(("TPE1", mutagen.id3.TPE1, self.resource.author.fullname))

        update_required = False
        for id3_tag, ID3Tag, value in id3_tags:
            if value in mediafile.tags.getall(id3_tag):
                continue
            mediafile.tags.add(ID3Tag(encoding=3, text=value))
            update_required = True

        if update_required:
            mediafile.tags.save(self.file.file.file)


def get_feed_artwork_filename(instance, filename):
    try:
        extension = "." + filename.split(".")[-1]
    except IndexError:
        extension = ""
    return "resource/feed/%s%s" % (instance.slug, extension)


class ResourceFeed(models.Model):
    title = models.CharField(max_length=64, verbose_name=_("title"))
    slug = models.SlugField(db_index=True, verbose_name=_("slug"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    tags = models.ManyToManyField(Tag, blank=True, related_name="feeds", verbose_name=_("tags"))
    show_children = models.BooleanField(default=False, verbose_name=_("show children"))
    mime_type_list = models.CharField(
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r"^([\w+-]+/[\w+-]+,)*([\w+-]+/[\w+-]+)?$")],
        max_length=256,
        verbose_name=_("MIME types"),
        help_text=_(
            "A comma-separated list of MIME types. Only items with attachments of"
            "the given MIME types will appear in the feed."
        ),
    )
    category_list = models.CharField(
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r"^([^,]+,)*([^,]+)?$")],
        max_length=256,
        verbose_name=_("categories"),
        help_text=_("A comma-separated list of category names to apply to the feed."),
    )
    copyright = models.CharField(null=True, blank=True, max_length=128, verbose_name=_("copyright"))
    artwork = models.FileField(null=True, blank=True, upload_to=get_feed_artwork_filename, verbose_name=_("artwork"))
    is_podcast = models.BooleanField(default=False, verbose_name=_("podcast"))
    owner_name = models.CharField(null=True, blank=True, max_length=64, verbose_name=_("owner name"))
    owner_email = models.CharField(null=True, blank=True, max_length=64, verbose_name=_("owner email"))

    class Meta:
        ordering = ["title"]
        verbose_name = _("feed")
        verbose_name_plural = _("feeds")

    def __str__(self):
        return self.title

    @cached_property
    def mime_types(self):
        return self.mime_type_list.split(",") if self.mime_type_list else []

    @cached_property
    def categories(self):
        return [c.strip() for c in self.category_list.split(",")] if self.category_list else []

    @cached_property
    def image_url(self):
        if self.artwork:
            return attachment_url(
                reverse("resources:feed_artwork", kwargs={"slug": self.slug}), self.artwork.file.name
            )
        return None


def get_featured_items(private=False):
    featured_items = list(
        chain(
            Tag.featured_objects.filter(is_private=private).only("slug", "name", "description", "priority"),
            (
                Resource.featured_objects.filter(is_published=True, is_private=private)
                .exclude(slug__in=Tag.featured_objects.values("slug"))
                .only("slug", "title", "description", "priority")
            ),
        )
    )
    try:
        featured_items.sort(key=lambda X: X.priority)
    except TypeError:
        logger.debug("Failed to sort featured items")

    return featured_items
