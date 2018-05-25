from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_localise_strings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='husband',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='+',
                to='directory.Person',
                verbose_name='husband',
            ),
        ),
        migrations.AlterField(
            model_name='family',
            name='wife',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='+',
                to='directory.Person',
                verbose_name='wife',
            ),
        ),
    ]
