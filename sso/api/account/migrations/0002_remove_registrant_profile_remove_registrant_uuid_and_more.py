# Generated by Django 4.0.4 on 2022-06-14 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrant',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='registrant',
            name='uuid',
        ),
        migrations.AlterField(
            model_name='registrant',
            name='mac',
            field=models.CharField(max_length=20, primary_key=True, serialize=False, verbose_name='Alamat MAC'),
        ),
    ]
