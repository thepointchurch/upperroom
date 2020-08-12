import django.db.models.deletion
from django.db import migrations, models

import thepoint.apps.weblog.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('directory', '0006_add_can_view_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeblogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('title', models.CharField(verbose_name='title',
                                           max_length=64)),
                ('slug', models.SlugField(verbose_name='slug',
                                          unique_for_month='created')),
                ('description', models.TextField(verbose_name='description',
                                                 null=True,
                                                 blank=True)),
                ('body', models.TextField(verbose_name='body',
                                          null=True,
                                          blank=True)),
                ('show_author', models.BooleanField(verbose_name='show author',
                                                    default=True)),
                ('created', models.DateTimeField(verbose_name='created',
                                                 auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='modified',
                                                  auto_now=True)),
                ('published', models.DateTimeField(verbose_name='published',
                                                   null=True,
                                                   blank=True)),
                ('show_date', models.BooleanField(verbose_name='show date',
                                                  default=True)),
                ('is_published', models.BooleanField(verbose_name='published',
                                                     default=False)),
                ('author', models.ForeignKey(verbose_name='author',
                                             related_name='weblogs',
                                             to='directory.Person',
                                             on_delete=django.db.models.deletion.SET_NULL,
                                             null=True,
                                             blank=True)),
            ],
            options={
                'ordering': ['-published'],
                'get_latest_by': 'published',
                'verbose_name': 'weblog entry',
                'verbose_name_plural': 'weblog entries',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False,
                                        auto_created=True,
                                        primary_key=True)),
                ('title', models.CharField(verbose_name='title',
                                           max_length=64)),
                ('slug', models.SlugField(verbose_name='slug')),
                ('file', models.FileField(verbose_name='file',
                                          upload_to=thepoint.apps.weblog.models.get_attachment_filename)),
                ('mime_type', models.CharField(verbose_name='MIME type',
                                               max_length=128,
                                               editable=False)),
                ('kind', models.CharField(verbose_name='kind',
                                          default='I',
                                          max_length=1,
                                          choices=[('A', 'Alternate'),
                                                   ('I', 'Inline')])),
                ('entry', models.ForeignKey(verbose_name='entry',
                                            related_name='attachments',
                                            to='weblog.WeblogEntry',
                                            on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
                'ordering': ['entry'],
                'unique_together': {('entry', 'slug')},
            },
        ),
    ]
