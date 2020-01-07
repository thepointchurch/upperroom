from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name=_('title'),
    )
    subtitle = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name=_('subtitle'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('description'),
    )
    type = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('type'),
    )
    author = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('author'),
    )
    isbn = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('ISBN'),
    )
    location = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('location'),
    )

    class Meta:
        ordering = ['title']
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __str__(self):
        return self.title

    @property
    def authors(self):
        return self.author.split('\n')
