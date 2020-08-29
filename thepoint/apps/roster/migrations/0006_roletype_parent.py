# pylint: disable=invalid-name
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0005_update_roles_relation"),
    ]

    operations = [
        migrations.AlterModelManagers(name="role", managers=[]),
        migrations.AddField(
            model_name="roletype",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="roster.RoleType",
                verbose_name="parent",
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="role",
            field=models.ForeignKey(
                limit_choices_to=models.Q(children__isnull=True),
                on_delete=django.db.models.deletion.PROTECT,
                related_name="roles",
                to="roster.RoleType",
                verbose_name="role",
            ),
        ),
    ]
