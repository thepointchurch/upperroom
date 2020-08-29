# pylint: disable=invalid-name
from django.db import migrations, models

import thepoint.apps.directory.models


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0004_surname_override"),
    ]

    operations = [
        migrations.AddField(
            model_name="family",
            name="photo",
            field=models.ImageField(
                blank=True, null=True, upload_to=thepoint.apps.directory.models.get_family_photo_filename
            ),
        ),
        migrations.AddField(
            model_name="family",
            name="photo_thumbnail",
            field=models.ImageField(
                blank=True,
                null=True,
                editable=False,
                upload_to=thepoint.apps.directory.models.get_family_thumbnail_filename,
            ),
        ),
    ]
