# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extendedsites", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="keyword", index=models.Index(fields=["order", "value"], name="extendedsit_order_4c95b0_idx"),
        ),
    ]
