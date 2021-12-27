# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weblog", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="attachment",
            index=models.Index(fields=["entry_id", "kind"], name="weblog_atta_entry_i_9e8c2b_idx"),
        ),
        migrations.AddIndex(
            model_name="weblogentry",
            index=models.Index(fields=["published"], name="weblog_webl_publish_d624e8_idx"),
        ),
        migrations.AddIndex(
            model_name="weblogentry",
            index=models.Index(fields=["is_published"], name="weblog_webl_is_publ_7ad033_idx"),
        ),
    ]
