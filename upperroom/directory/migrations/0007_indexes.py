# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0006_add_can_view_permission"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="family",
            index=models.Index(fields=["name"], name="directory_f_name_bfadf2_idx"),
        ),
        migrations.AddIndex(
            model_name="family",
            index=models.Index(fields=["is_current"], name="directory_f_is_curr_c02057_idx"),
        ),
        migrations.AddIndex(
            model_name="person",
            index=models.Index(fields=["order", "id", "name"], name="directory_p_order_44e645_idx"),
        ),
        migrations.AddIndex(
            model_name="person",
            index=models.Index(fields=["is_current"], name="directory_p_is_curr_efb218_idx"),
        ),
    ]
