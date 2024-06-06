# Generated by Django 5.0.6 on 2024-06-06 17:09

import app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_customersatisfactionsurvey_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='customer',
            field=models.ForeignKey(blank=True, default=app.models.get_default_customer, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.customer'),
        ),
    ]
