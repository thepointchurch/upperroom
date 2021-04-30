# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0003_rename_files"),
    ]

    operations = [
        migrations.RunSQL(sql="DROP VIEW IF EXISTS resources_featureditem;",),
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
        migrations.RunSQL(
            sql=[
                "DROP VIEW IF EXISTS resources_featureditem;",
                """CREATE VIEW resources_featureditem AS
                   SELECT title,
                       slug,
                       description,
                       priority,
                       is_private,
                       'R' AS type
                   FROM resources_resource WHERE priority IS NOT NULL AND is_published
                   UNION
                   SELECT name AS title,
                       slug,
                       description,
                       priority,
                       is_private,
                       'T' AS type
                   FROM resources_tag WHERE priority IS NOT NULL;""",
            ],
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
