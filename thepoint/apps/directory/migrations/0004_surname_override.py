# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0003_set_on_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="surname_override",
            field=models.CharField(blank=True, null=True, max_length=30, verbose_name="surname"),
        ),
    ]
