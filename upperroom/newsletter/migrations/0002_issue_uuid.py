# pylint: disable=invalid-name

import uuid

from django.db import migrations, models
from django.db.utils import OperationalError


def set_uuid(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Issue = apps.get_model("newsletter", "Issue")
    for obj in Issue.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


def remove_old_primary_key(apps, schema_editor):
    Issue = apps.get_model("newsletter", "Issue")
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, Issue._meta.db_table)
    key_constraint = None
    for constraint_name, constraint in constraints.items():
        if constraint.get("primary_key"):
            key_constraint = constraint_name
            break
    else:
        raise Exception("Missing primary key constraint")
    quote_name = connection.ops.quote_name
    try:
        schema_editor.execute(
            schema_editor.sql_delete_pk
            % {"table": quote_name(Issue._meta.db_table), "name": quote_name(key_constraint)}
        )
    except OperationalError:
        pass  # assume the DB was SQLite


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0001_squashed_0005_indexes"),
    ]

    operations = [
        migrations.AddField(model_name="issue", name="uuid", field=models.UUIDField(null=True)),
        migrations.RunPython(set_uuid, migrations.RunPython.noop),
        migrations.RunPython(remove_old_primary_key),
        migrations.AlterField(
            model_name="issue",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="issue", name="id"),
        migrations.RenameField(model_name="issue", old_name="uuid", new_name="id"),
    ]
