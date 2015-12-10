import logging
import magic
import mimetypes
from itertools import chain

from django.core.urlresolvers import resolve, reverse
from django.db import models
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from directory.models import Person


logger = logging.getLogger(__name__)


class FeaturedMixin(models.Model):
    priority = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text=_('A non-empty value will feature this item '
                    'in the main menu.'))

    class Meta:
        abstract = True

    @property
    def is_featured(self):
        return self.priority is not None


class FeaturedManager(models.Manager):
    def get_queryset(self):
        return super(FeaturedManager,
                     self).get_queryset().filter(priority__isnull=False)


class Tag(FeaturedMixin, models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)

    resources_per_page = models.PositiveSmallIntegerField(default=10,
                                                          null=True,
                                                          blank=True)
    reverse_order = models.BooleanField(default=False)
    show_date = models.BooleanField(default=True)

    # Items with an exclusive tag only appear when searching for this tag.
    is_exclusive = models.BooleanField(default=False,
                                       verbose_name='Exclusive')

    objects = models.Manager()
    featured_objects = FeaturedManager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name

    def get_absolute_url(self):
        # should we search for conflicting URLs?
        if self.is_featured:
            url = '/%s/' % self.slug
            try:
                resolve(url)
            except Http404:
                return url
        return reverse('resources:tag', kwargs={'slug': self.slug})


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,
                     self).get_queryset().filter(is_published=True)


class Resource(FeaturedMixin, models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True,
                                  related_name='resources')

    author = models.ForeignKey(Person, null=True, blank=True,
                               related_name='resources')
    show_author = models.BooleanField(default=True)

    parent = models.ForeignKey('self', null=True, blank=True,
                               related_name='children')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    show_date = models.BooleanField(default=True)

    is_published = models.BooleanField(default=False, verbose_name='Published')
    is_private = models.BooleanField(default=False, verbose_name='Private')

    objects = models.Manager()
    published_objects = PublishedManager()
    featured_objects = FeaturedManager()

    class Meta:
        ordering = ['created']
        get_latest_by = 'created'
        verbose_name_plural = 'resources'

    def __str__(self):
        return self.title

    @property
    def alternates(self):
        return self.attachments.filter(kind=Attachment.KIND_ALTERNATE)

    @property
    def inlines(self):
        return self.attachments.filter(kind=Attachment.KIND_INLINE)

    @property
    def content(self):
        content = self.body
        content += '\n'
        for child in self.children.all():
            content += '\n%s' % child.markdown_link()
        for attachment in self.inlines:
            content += '\n%s' % attachment.markdown_link()
        return content

    def get_absolute_url(self):
        # should we search for conflicting URLs?
        if self.is_featured:
            url = '/%s' % self.slug
            try:
                resolve(url)
            except Http404:
                return url
        return reverse('resources:detail', kwargs={'slug': self.slug})

    def markdown_link(self):
        return '[%s]: %s' % (self.title, reverse('resources:detail',
                                                 kwargs={'slug': self.slug}))


def get_attachment_filename(instance, filename):
    return 'resource/attachment/%s/%s%s' % (instance.resource.slug,
                                            instance.slug,
                                            instance.extension)


class Attachment(models.Model):
    KIND_ALTERNATE = 'A'
    KIND_INLINE = 'I'
    KIND_CHOICES = (
        (KIND_ALTERNATE, 'Alternate'),
        (KIND_INLINE, 'Inline'),
    )

    _utf_translate = str.maketrans(
        '\u2013\u201c\u201d',
        '-""'
    )

    title = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True)
    file = models.FileField(upload_to=get_attachment_filename)
    mime_type = models.CharField(max_length=128, editable=False)
    kind = models.CharField(max_length=1, choices=KIND_CHOICES,
                            default=KIND_INLINE)
    description = models.TextField(null=True, blank=True)
    resource = models.ForeignKey(Resource, related_name='attachments')

    class Meta:
        ordering = ['resource']
        verbose_name_plural = 'attachments'
        unique_together = ('resource', 'slug')

    def __str__(self):
        return self.title

    def clean(self):
        uploaded_content_type = getattr(self.file, 'content_type', '')
        self.file.seek(0)
        magic_content_type = magic.from_buffer(self.file.read(),
                                               mime=True).decode()
        self.file.seek(0)

        # Prefer magic mime-type instead mime-type from http header
        if uploaded_content_type != magic_content_type:
            uploaded_content_type = magic_content_type

        self.mime_type = uploaded_content_type

    @property
    def clean_title(self):
        return self.title.translate(Attachment._utf_translate)

    @property
    def extension(self):
        try:
            return [t for t in mimetypes.guess_all_extensions(self.mime_type)
                    if t not in ['.jpe', '.pwz']][0]
        except IndexError:
            return None

    @property
    def format(self):
        if self.extension:
            return self.extension.lstrip('.').upper()
        else:
            return 'Unknown'

    @property
    def is_private(self):
        return self.resource.is_private

    def markdown_link(self):
        return '[%s]: %s' % (self.title, reverse('resources:attachment',
                                                 kwargs={'pk': self.id}))


def get_featured_items():
    featured_items = list(chain(
        Tag.featured_objects.all(),
        Resource.featured_objects.filter(is_published=True, is_private=False)
    ))
    try:
        featured_items.sort(key=lambda X: X.priority)
    except TypeError:
        logger.debug('Failed to sort featured items')

    return featured_items


def get_featured_private_items():
    return Resource.featured_objects.filter(
        is_published=True, is_private=True).order_by('priority')
