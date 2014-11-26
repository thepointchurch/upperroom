# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import roster.models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'locations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=roster.models.next_meeting, unique=True)),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
                'verbose_name_plural': 'meetings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('revision', models.PositiveIntegerField(default=0)),
                ('guest', models.CharField(max_length=30, null=True, blank=True)),
                ('description', models.CharField(max_length=64, null=True, blank=True)),
                ('location', models.ForeignKey(related_name='roles', blank=True, to='roster.Location', null=True)),
                ('meeting', models.ForeignKey(related_name='roles', to='roster.Meeting')),
                ('person', models.ForeignKey(related_name='roles', blank=True, to='directory.Person', null=True)),
            ],
            options={
                'ordering': ['role', 'person__name'],
                'verbose_name_plural': 'roles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('verb', models.CharField(max_length=30)),
                ('order', models.PositiveSmallIntegerField(default=100)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name_plural': 'roletypes',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='role',
            name='role',
            field=models.ForeignKey(related_name='roles', to='roster.RoleType'),
            preserve_default=True,
        ),
    ]
