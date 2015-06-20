# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import roster.models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'locations',
            },
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('date', models.DateField(
                    default=roster.models.next_empty_meeting_date,
                    unique=True)),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
                'verbose_name_plural': 'meetings',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('revision', models.PositiveIntegerField(default=0)),
                ('guest', models.CharField(max_length=30,
                                           null=True,
                                           blank=True)),
                ('description', models.CharField(max_length=64,
                                                 null=True,
                                                 blank=True)),
                ('location', models.ForeignKey(related_name='roles',
                                               to='roster.Location',
                                               null=True,
                                               blank=True)),
                ('meeting', models.ForeignKey(related_name='roles',
                                              to='roster.Meeting')),
                ('people', models.ManyToManyField(related_name='roles',
                                                  to='directory.Person',
                                                  blank=True)),
            ],
            options={
                'ordering': ['role'],
                'verbose_name_plural': 'roles',
            },
        ),
        migrations.CreateModel(
            name='RoleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('verb', models.CharField(max_length=50)),
                ('order', models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name_plural': 'roletypes',
            },
        ),
        migrations.AddField(
            model_name='role',
            name='role',
            field=models.ForeignKey(related_name='roles',
                                    to='roster.RoleType'),
        ),
    ]
