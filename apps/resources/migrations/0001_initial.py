# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import resources.models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField()),
                ('file', models.FileField(upload_to=resources.models.get_attachment_filename)),  # noqa
                ('mime_type', models.CharField(max_length=128,
                                               editable=False)),
                ('kind', models.CharField(default='I',
                                          max_length=1,
                                          choices=[('A', 'Alternate'),
                                                   ('I', 'Inline')])),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ['resource'],
                'verbose_name_plural': 'attachments',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('body', models.TextField(null=True, blank=True)),
                ('show_author', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_published',
                    models.BooleanField(default=False,
                                        verbose_name='Published')),
                ('is_private', models.BooleanField(default=False,
                                                   verbose_name='Private')),
                ('author', models.ForeignKey(related_name='resources',
                                             to='directory.Person',
                                             null=True,
                                             blank=True)),
                ('parent', models.ForeignKey(related_name='children',
                                             to='resources.Resource',
                                             null=True,
                                             blank=True)),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': 'created',
                'verbose_name_plural': 'resources',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(unique=True)),
                ('resources_per_page',
                    models.PositiveSmallIntegerField(default=10,
                                                     null=True,
                                                     blank=True)),
                ('reverse_order', models.BooleanField(default=False)),
                ('is_exclusive',
                    models.BooleanField(default=False,
                                        verbose_name='Exclusive')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'tags',
            },
        ),
        migrations.AddField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources',
                                         to='resources.Tag',
                                         blank=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='resource',
            field=models.ForeignKey(related_name='attachments',
                                    to='resources.Resource'),
        ),
        migrations.AlterUniqueTogether(
            name='attachment',
            unique_together=set([('resource', 'slug')]),
        ),
    ]
