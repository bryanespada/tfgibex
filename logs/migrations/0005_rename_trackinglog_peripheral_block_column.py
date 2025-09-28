from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0004_rename_foreign_key_columns'),
        ('appmodels', '0007_rename_peripheralblock_to_empresa'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE logs_trackinglog CHANGE COLUMN peripheral_block_id empresa_id BIGINT NULL;",
            reverse_sql="ALTER TABLE logs_trackinglog CHANGE COLUMN empresa_id peripheral_block_id BIGINT NULL;",
        ),
    ]