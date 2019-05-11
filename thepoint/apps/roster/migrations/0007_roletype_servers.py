from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0004_surname_override'),
        ('roster', '0006_roletype_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='roletype',
            name='servers',
            field=models.ManyToManyField(blank=True,
                                         limit_choices_to={'is_current': True},
                                         related_name='role_types',
                                         to='directory.Person',
                                         verbose_name='servers'),
        ),
    ]
