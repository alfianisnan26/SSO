# Generated by Django 4.0.4 on 2022-07-04 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='generation',
            name='is_graduated',
            field=models.BooleanField(default=False),
        ),
    ]