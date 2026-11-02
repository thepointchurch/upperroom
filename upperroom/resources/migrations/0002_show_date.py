# pylint: disable=invalid-name


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0001_initial"),
    ]

    operations = [
        migrations.AddField(model_name="tag", name="show_date", field=models.BooleanField(default=True)),
        migrations.AddField(model_name="resource", name="show_date", field=models.BooleanField(default=True)),
    ]
