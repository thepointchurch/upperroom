# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="family", options={"ordering": ["name"], "verbose_name": "family", "verbose_name_plural": "families"},
        ),
        migrations.AlterModelOptions(
            name="person",
            options={"ordering": ["order", "id", "name"], "verbose_name": "person", "verbose_name_plural": "people"},
        ),
        migrations.AlterField(
            model_name="family",
            name="anniversary",
            field=models.DateField(verbose_name="anniversary", blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="family",
            name="email",
            field=models.EmailField(verbose_name="email", blank=True, null=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="family",
            name="husband",
            field=models.ForeignKey(
                blank=True,
                related_name="+",
                verbose_name="husband",
                to="directory.Person",
                on_delete=models.SET_NULL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="family", name="is_current", field=models.BooleanField(verbose_name="current", default=True),
        ),
        migrations.AlterField(
            model_name="family", name="name", field=models.CharField(verbose_name="name", max_length=30),
        ),
        migrations.AlterField(
            model_name="family",
            name="phone_home",
            field=models.CharField(verbose_name="home phone", blank=True, null=True, max_length=15),
        ),
        migrations.AlterField(
            model_name="family",
            name="phone_mobile",
            field=models.CharField(verbose_name="mobile phone", blank=True, null=True, max_length=15),
        ),
        migrations.AlterField(
            model_name="family",
            name="postcode",
            field=models.CharField(verbose_name="postcode", blank=True, null=True, max_length=6),
        ),
        migrations.AlterField(
            model_name="family",
            name="street",
            field=models.CharField(verbose_name="street", blank=True, null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name="family",
            name="suburb",
            field=models.CharField(verbose_name="suburb", blank=True, null=True, max_length=32),
        ),
        migrations.AlterField(
            model_name="family",
            name="wife",
            field=models.ForeignKey(
                blank=True,
                related_name="+",
                verbose_name="wife",
                to="directory.Person",
                on_delete=models.SET_NULL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="birthday",
            field=models.DateField(verbose_name="birthday", blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="email",
            field=models.EmailField(verbose_name="email", blank=True, null=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="person",
            name="family",
            field=models.ForeignKey(
                related_name="members", verbose_name="family", to="directory.Family", on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="gender",
            field=models.CharField(
                choices=[("M", "Male"), ("F", "Female")], verbose_name="gender", blank=True, null=True, max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="person", name="is_current", field=models.BooleanField(verbose_name="current", default=True),
        ),
        migrations.AlterField(
            model_name="person", name="is_member", field=models.BooleanField(verbose_name="member", default=True),
        ),
        migrations.AlterField(
            model_name="person", name="name", field=models.CharField(verbose_name="name", max_length=30),
        ),
        migrations.AlterField(
            model_name="person",
            name="order",
            field=models.SmallIntegerField(verbose_name="order", blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="phone_mobile",
            field=models.CharField(verbose_name="mobile phone", blank=True, null=True, max_length=15),
        ),
        migrations.AlterField(
            model_name="person",
            name="phone_work",
            field=models.CharField(verbose_name="work phone", blank=True, null=True, max_length=15),
        ),
        migrations.AlterField(
            model_name="person",
            name="suffix",
            field=models.CharField(verbose_name="suffix", blank=True, null=True, max_length=3),
        ),
        migrations.AlterField(
            model_name="person",
            name="user",
            field=models.OneToOneField(
                blank=True, verbose_name="user", to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
            ),
        ),
    ]
