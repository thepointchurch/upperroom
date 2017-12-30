# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime

import thepoint.apps.newsletter as newsletter


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={
                'ordering': ['-date'],
                'get_latest_by': 'date',
                'verbose_name': 'issue',
                'verbose_name_plural': 'issues',
            },
        ),
        migrations.AlterModelOptions(
            name='publication',
            options={
                'ordering': ['name'],
                'verbose_name': 'publication',
                'verbose_name_plural': 'publications',
            },
        ),
        migrations.AlterField(
            model_name='issue',
            name='date',
            field=models.DateField(
                default=datetime.date.today,
                verbose_name='date',
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=models.TextField(
                verbose_name='description',
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='file',
            field=models.FileField(
                verbose_name='file',
                upload_to=newsletter.models.get_filename,
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='mime_type',
            field=models.CharField(
                editable=False,
                verbose_name='MIME type',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='slug',
            field=models.SlugField(
                verbose_name='slug',
                editable=False,
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='description',
            field=models.TextField(
                verbose_name='description',
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='is_private',
            field=models.BooleanField(
                default=False,
                verbose_name='private',
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='mime_types',
            field=models.CharField(
                verbose_name='MIME types',
                max_length=256,
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='name',
            field=models.CharField(
                verbose_name='name',
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='publication_day',
            field=models.CharField(
                choices=[
                    ('0', 'Monday'),
                    ('1', 'Tuesday'),
                    ('2', 'Wednesday'),
                    ('3', 'Thursday'),
                    ('4', 'Friday'),
                    ('5', 'Saturday'),
                    ('6', 'Sunday'),
                ],
                verbose_name='publication day',
                max_length=1,
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='publication',
            name='slug',
            field=models.SlugField(
                verbose_name='slug',
                unique=True,
            ),
        ),
    ]
