from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0010_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='metadata',
            field=models.JSONField(verbose_name='metadata',
                                   null=True,
                                   blank=True),
        ),
    ]
