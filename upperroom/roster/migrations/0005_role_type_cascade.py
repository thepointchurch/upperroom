# pylint: disable=invalid-name
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0004_roster_exclusions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="role",
            field=models.ForeignKey(
                limit_choices_to=models.Q(("children__isnull", True)),
                on_delete=django.db.models.deletion.CASCADE,
                related_name="roles",
                to="roster.roletype",
                verbose_name="role",
            ),
        ),
    ]
