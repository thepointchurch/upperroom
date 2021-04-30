# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0001_squashed_0002_localise_strings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
