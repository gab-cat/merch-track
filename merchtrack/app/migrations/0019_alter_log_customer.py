# Generated by Django 5.0.6 on 2024-06-06 17:22

import app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_alter_log_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='customer',
            field=models.ForeignKey(default=app.models.get_default_customer, on_delete=django.db.models.deletion.CASCADE, to='app.customer'),
        ),
    ]
