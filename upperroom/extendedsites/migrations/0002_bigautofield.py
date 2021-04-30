# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extendedsites", "0001_squashed_0002_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="keyword",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
