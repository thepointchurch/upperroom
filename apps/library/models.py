from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=64, null=True, blank=True)
    author = models.CharField(max_length=128, null=True, blank=True)
    isbn = models.CharField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'books'

    def __str__(self):
        return self.title

    @property
    def authors(self):
        return self.author.split('\n')
