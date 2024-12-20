# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("roster", "0002_bigautofield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="name",
            field=models.CharField(max_length=128, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="meetingtemplate",
            name="name",
            field=models.CharField(max_length=64, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="role",
            name="description",
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="role",
            name="guest",
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="guest"),
        ),
        migrations.AlterField(
            model_name="roletype",
            name="name",
            field=models.CharField(max_length=128, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="roletype",
            name="verb",
            field=models.CharField(max_length=128, verbose_name="verb"),
        ),
    ]
