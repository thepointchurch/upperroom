from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0010_roletype_include_in_print'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='roletype',
            index=models.Index(fields=['order'], name='roster_role_order_42d3b6_idx'),
        ),
    ]
