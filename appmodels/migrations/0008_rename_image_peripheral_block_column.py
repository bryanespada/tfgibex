from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0007_rename_peripheralblock_to_empresa'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE appmodels_image CHANGE COLUMN peripheral_block_id empresa_id BIGINT NULL;",
            reverse_sql="ALTER TABLE appmodels_image CHANGE COLUMN empresa_id peripheral_block_id BIGINT NULL;",
        ),
    ]