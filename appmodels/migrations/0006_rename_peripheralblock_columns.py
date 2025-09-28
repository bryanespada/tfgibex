from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0005_rename_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE appmodels_peripheralblock CHANGE COLUMN surgery_type_id bolsa_id BIGINT NOT NULL;",
            reverse_sql="ALTER TABLE appmodels_peripheralblock CHANGE COLUMN bolsa_id surgery_type_id BIGINT NOT NULL;",
        ),
    ]