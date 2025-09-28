from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0006_rename_peripheralblock_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="RENAME TABLE appmodels_peripheralblock TO appmodels_empresa;",
            reverse_sql="RENAME TABLE appmodels_empresa TO appmodels_peripheralblock;",
        ),
    ]