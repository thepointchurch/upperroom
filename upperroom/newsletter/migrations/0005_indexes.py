# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0004_set_on_delete"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["date"], name="newsletter__date_969234_idx"),
        ),
    ]
