import fnmatch
import mimetypes
import re
from datetime import date, timedelta

import magic
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


def get_filename(instance, filename):
    return 'newsletter/%s/%s/%s%s' % (instance.publication.slug,
                                      instance.date.year,
                                      instance.date,
                                      instance.extension)


def default_publication():
    try:
        return Publication.objects.first().pk
    except:
        return None


class Publication(models.Model):
    DAYS_OF_WEEK = (
        ('0', _('Monday')),
        ('1', _('Tuesday')),
        ('2', _('Wednesday')),
        ('3', _('Thursday')),
        ('4', _('Friday')),
        ('5', _('Saturday')),
        ('6', _('Sunday')),
    )

    slug = models.SlugField(
        unique=True,
        verbose_name=_('slug'),
    )
    name = models.CharField(
        max_length=64,
        verbose_name=_('name'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description'),
    )
    mime_types = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name=_('MIME types'),
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('private'),
    )
    publication_day = models.CharField(
        max_length=1,
        choices=DAYS_OF_WEEK,
        null=True,
        blank=True,
        verbose_name=_('publication day'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('publication')
        verbose_name_plural = _('publications')

    def __str__(self):
        return self.name

    def accept_mime_type(self, mime_type):
        if not self.mime_types:
            return True

        types = re.split(r'\s+', self.mime_types)
        for type in types:
            if fnmatch.fnmatch(mime_type, type):
                return True

        return False

    def correct_publication_date(self, date):
        try:
            day = int(self.publication_day)
        except (TypeError, ValueError):
            return date

        if date.weekday != day:
            date += timedelta(day - date.weekday())
        return date


class Issue(models.Model):
    date = models.DateField(
        default=date.today,
        verbose_name=_('date'),
    )
    slug = models.SlugField(
        editable=False,
        verbose_name=_('slug'),
    )
    file = models.FileField(
        upload_to=get_filename,
        verbose_name=_('file'),
    )
    mime_type = models.CharField(
        max_length=128,
        editable=False,
        verbose_name=_('MIME type'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description'),
    )

    publication = models.ForeignKey(
        Publication,
        on_delete=models.PROTECT,
        related_name='issues',
        unique_for_date='date',
        default=default_publication,
        verbose_name=_('publication'),
    )

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'
        verbose_name = _('issue')
        verbose_name_plural = _('issues')

    def __str__(self):
        return str(self.date)

    def clean(self):
        self.date = self.publication.correct_publication_date(self.date)
        self.slug = str(self.date)

        uploaded_content_type = getattr(self.file, 'content_type', '')
        self.file.seek(0)
        magic_content_type = magic.from_buffer(self.file.read(),
                                               mime=True).decode()
        self.file.seek(0)

        # Prefer magic mime-type instead mime-type from http header
        if uploaded_content_type != magic_content_type:
            uploaded_content_type = magic_content_type

        self.mime_type = uploaded_content_type

        if not self.publication.accept_mime_type(self.mime_type):
            raise ValidationError('Files of type %s are not supported.'
                                  % uploaded_content_type)

    @property
    def extension(self):
        try:
            return [t for t in mimetypes.guess_all_extensions(self.mime_type)
                    if t not in ['.jpe']][0]
        except IndexError:
            return None

    @property
    def is_private(self):
        return self.publication.is_private
