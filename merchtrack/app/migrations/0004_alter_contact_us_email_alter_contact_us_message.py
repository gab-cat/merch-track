# Generated by Django 4.2.13 on 2024-05-18 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_contact_us_user_info_course_user_info_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact_us',
            name='email',
            field=models.EmailField(max_length=200),
        ),
        migrations.AlterField(
            model_name='contact_us',
            name='message',
            field=models.TextField(max_length=200),
        ),
    ]