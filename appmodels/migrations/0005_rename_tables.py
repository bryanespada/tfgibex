from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0004_alter_generalconfig_paypal_account_email_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="RENAME TABLE appmodels_surgerytype TO appmodels_bolsa;",
            reverse_sql="RENAME TABLE appmodels_bolsa TO appmodels_surgerytype;",
        ),
    ]