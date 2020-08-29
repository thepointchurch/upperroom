# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("splash", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="splash",
            index=models.Index(fields=["is_current", "position"], name="splash_spla_is_curr_f96f12_idx"),
        ),
        migrations.AddIndex(
            model_name="splash",
            index=models.Index(fields=["url", "position", "order", "title"], name="splash_spla_url_e4ebd5_idx"),
        ),
    ]
