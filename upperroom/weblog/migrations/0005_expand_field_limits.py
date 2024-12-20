# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblog", "0004_bigautofield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="title",
            field=models.CharField(max_length=128, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="weblogentry",
            name="title",
            field=models.CharField(max_length=128, verbose_name="title"),
        ),
    ]
