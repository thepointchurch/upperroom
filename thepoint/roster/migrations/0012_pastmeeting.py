# pylint: disable=invalid-name
import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0011_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="PastMeeting",
            fields=[],
            options={"proxy": True, "indexes": [], "constraints": []},
            bases=("roster.meeting",),
            managers=[("current_objects", django.db.models.manager.Manager())],
        ),
    ]
