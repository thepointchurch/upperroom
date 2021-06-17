# pylint: disable=invalid-name

from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):
    dependencies = [("resources", "0011_jsonfield")]
    operations = [
        migrations.RunSQL(sql=SQL_CREATE, reverse_sql=SQL_DROP),
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
