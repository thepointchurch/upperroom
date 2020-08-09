from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblog', '0002_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='description',
            field=models.TextField(verbose_name='description',
                                   null=True,
                                   blank=True),
        ),
    ]
