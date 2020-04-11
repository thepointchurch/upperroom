from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0005_add_photos'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='family',
            options={'ordering': ['name'],
                     'permissions': [('can_view', 'Can view the directory')],
                     'verbose_name': 'family',
                     'verbose_name_plural': 'families'},
        ),
    ]
