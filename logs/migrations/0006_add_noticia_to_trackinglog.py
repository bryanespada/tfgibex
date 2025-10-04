# Generated manually for adding noticia field to TrackingLog
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appmodels', '0001_initial'),
        ('logs', '0005_rename_trackinglog_peripheral_block_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackinglog',
            name='noticia',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='appmodels.noticia'),
        ),
    ]