# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("splash", "0002_bigautofield"),
    ]

    operations = [
        migrations.AlterField(
            model_name="splash",
            name="url",
            field=models.CharField(default="/", max_length=128),
        ),
    ]
