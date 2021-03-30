# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0008_meeting_templates"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtemplate",
            name="is_default",
            field=models.BooleanField(default=False, verbose_name="is default"),
        ),
        migrations.AddField(
            model_name="roletype",
            name="order_by_age",
            field=models.BooleanField(default=True, verbose_name="order by age"),
        ),
    ]
