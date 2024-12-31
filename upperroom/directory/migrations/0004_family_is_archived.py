# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("directory", "0003_expand_field_limits"),
    ]

    operations = [
        migrations.AddField(
            model_name="family",
            name="is_archived",
            field=models.BooleanField(default=False, verbose_name="archived"),
        ),
    ]
