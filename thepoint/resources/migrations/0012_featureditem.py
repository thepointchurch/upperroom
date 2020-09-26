# pylint: disable=invalid-name

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("resources", "0011_jsonfield")]
    operations = [
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
            reverse_sql="DROP VIEW IF EXISTS resources_featureditem;",
        ),
        migrations.CreateModel(
            name="FeaturedItem",
            fields=[
                ("title", models.CharField(max_length=64)),
                ("slug", models.SlugField(primary_key=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("priority", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_private", models.BooleanField()),
                ("type", models.CharField(max_length=1, choices=[("R", "Resource"), ("T", "Tag")])),
            ],
            options={"db_table": "resources_featureditem", "managed": False},
        ),
    ]
