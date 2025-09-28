from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0003_alter_subscriptionlog_payload_and_more'),
        ('appmodels', '0004_rename_surgicalarea_to_mercado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trackinglog',
            old_name='surgical_area',
            new_name='mercado',
        ),
    ]