# pylint: disable=invalid-name
from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0007_resource_is_pinned"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP),
        migrations.AlterField(
            model_name="attachment",
            name="title",
            field=models.CharField(max_length=128, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="title",
            field=models.CharField(max_length=128, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="copyright",
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name="copyright"),
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="owner_email",
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="owner email"),
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="owner_name",
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name="owner name"),
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="title",
            field=models.CharField(max_length=128, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(max_length=128, verbose_name="name"),
        ),
        migrations.RunSQL(sql=SQL_CREATE),
    ]
