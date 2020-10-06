# pylint: disable=invalid-name

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import thepoint.directory.models


class Migration(migrations.Migration):

    replaces = [
        ("directory", "0001_initial"),
        ("directory", "0002_localise_strings"),
        ("directory", "0003_set_on_delete"),
        ("directory", "0004_surname_override"),
        ("directory", "0005_add_photos"),
        ("directory", "0006_add_can_view_permission"),
        ("directory", "0007_indexes"),
    ]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Family",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
                ("phone_home", models.CharField(blank=True, max_length=15, null=True, verbose_name="home phone")),
                ("phone_mobile", models.CharField(blank=True, max_length=15, null=True, verbose_name="mobile phone")),
                ("email", models.EmailField(blank=True, max_length=254, null=True, verbose_name="email")),
                ("street", models.CharField(blank=True, max_length=128, null=True, verbose_name="street")),
                ("suburb", models.CharField(blank=True, max_length=32, null=True, verbose_name="suburb")),
                ("postcode", models.CharField(blank=True, max_length=6, null=True, verbose_name="postcode")),
                ("is_current", models.BooleanField(default=True, verbose_name="current")),
                ("anniversary", models.DateField(blank=True, null=True, verbose_name="anniversary")),
                (
                    "photo",
                    models.ImageField(
                        blank=True, null=True, upload_to=thepoint.directory.models.get_family_photo_filename
                    ),
                ),
                (
                    "photo_thumbnail",
                    models.ImageField(
                        blank=True,
                        editable=False,
                        null=True,
                        upload_to=thepoint.directory.models.get_family_thumbnail_filename,
                    ),
                ),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "families"},
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.SmallIntegerField(blank=True, null=True, verbose_name="order")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
                ("suffix", models.CharField(blank=True, max_length=3, null=True, verbose_name="suffix")),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("M", "Male"), ("F", "Female")],
                        max_length=1,
                        null=True,
                        verbose_name="gender",
                    ),
                ),
                ("birthday", models.DateField(blank=True, null=True, verbose_name="birthday")),
                ("email", models.EmailField(blank=True, max_length=254, null=True, verbose_name="email")),
                ("phone_mobile", models.CharField(blank=True, max_length=15, null=True, verbose_name="mobile phone")),
                ("phone_work", models.CharField(blank=True, max_length=15, null=True, verbose_name="work phone")),
                ("is_member", models.BooleanField(default=True, verbose_name="member")),
                ("is_current", models.BooleanField(default=True, verbose_name="current")),
                (
                    "family",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="directory.family",
                        verbose_name="family",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
                ("surname_override", models.CharField(blank=True, max_length=30, null=True, verbose_name="surname")),
            ],
            options={"ordering": ["order", "id", "name"], "verbose_name_plural": "people", "verbose_name": "person"},
        ),
        migrations.AddField(
            model_name="family",
            name="husband",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="directory.person",
                verbose_name="husband",
            ),
        ),
        migrations.AddField(
            model_name="family",
            name="wife",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="directory.person",
                verbose_name="wife",
            ),
        ),
        migrations.AlterModelOptions(
            name="family", options={"ordering": ["name"], "verbose_name": "family", "verbose_name_plural": "families"},
        ),
        migrations.AlterModelOptions(
            name="family",
            options={
                "ordering": ["name"],
                "permissions": [("can_view", "Can view the directory")],
                "verbose_name": "family",
                "verbose_name_plural": "families",
            },
        ),
        migrations.AddIndex(
            model_name="family", index=models.Index(fields=["name"], name="directory_f_name_bfadf2_idx"),
        ),
        migrations.AddIndex(
            model_name="family", index=models.Index(fields=["is_current"], name="directory_f_is_curr_c02057_idx"),
        ),
        migrations.AddIndex(
            model_name="person",
            index=models.Index(fields=["order", "id", "name"], name="directory_p_order_44e645_idx"),
        ),
        migrations.AddIndex(
            model_name="person", index=models.Index(fields=["is_current"], name="directory_p_is_curr_efb218_idx"),
        ),
    ]
