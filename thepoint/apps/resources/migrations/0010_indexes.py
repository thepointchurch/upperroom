from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0009_tag_is_private'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='attachment',
            index=models.Index(fields=['kind'], name='resources_a_kind_34af54_idx'),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=models.Index(fields=['published'], name='resources_r_publish_bb2046_idx'),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=models.Index(fields=['is_published'], name='resources_r_is_publ_7afbcf_idx'),
        ),
        migrations.AddIndex(
            model_name='resource',
            index=models.Index(fields=['is_private'], name='resources_r_is_priv_ae0b21_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['name'], name='resources_t_name_352b9c_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['is_exclusive'], name='resources_t_is_excl_1f4322_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['is_private'], name='resources_t_is_priv_0f2454_idx'),
        ),
    ]
