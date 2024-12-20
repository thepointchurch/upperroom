# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("directory", "0002_bigautofield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="family",
            name="name",
            field=models.CharField(max_length=64, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="family",
            name="suburb",
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="suburb"),
        ),
        migrations.AlterField(
            model_name="person",
            name="name",
            field=models.CharField(max_length=64, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="person",
            name="suffix",
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name="suffix"),
        ),
        migrations.AlterField(
            model_name="person",
            name="surname_override",
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name="surname"),
        ),
    ]
