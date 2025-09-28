from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0003_alter_subscription_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SurgicalArea',
            new_name='Mercado',
        ),
        migrations.RenameField(
            model_name='surgerytype',
            old_name='surgical_area',
            new_name='mercado',
        ),
    ]