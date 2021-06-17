# pylint: disable=invalid-name
from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0003_rename_files"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP),
        migrations.AlterField(
            model_name="resource",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.RunSQL(sql=SQL_CREATE),
        migrations.AlterField(
            model_name="resourcefeed",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
