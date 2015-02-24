# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('subtitle', models.CharField(max_length=128,
                                              null=True,
                                              blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=64,
                                          null=True,
                                          blank=True)),
                ('author', models.CharField(max_length=64,
                                            null=True,
                                            blank=True)),
                ('isbn', models.CharField(max_length=20,
                                          null=True,
                                          blank=True)),
                ('location', models.CharField(max_length=64,
                                              null=True,
                                              blank=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name_plural': 'books',
            },
            bases=(models.Model,),
        ),
    ]
