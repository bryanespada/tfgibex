from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0003_alter_subscriptionlog_payload_and_more'),
        ('appmodels', '0005_rename_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE logs_trackinglog CHANGE COLUMN surgery_type_id bolsa_id BIGINT NULL;",
            reverse_sql="ALTER TABLE logs_trackinglog CHANGE COLUMN bolsa_id surgery_type_id BIGINT NULL;",
        ),
    ]