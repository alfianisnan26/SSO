# Generated by Django 4.0.4 on 2022-06-11 03:26

from django.db import migrations, models
import imagekit.models.fields
import sso.api.res.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Background',
            fields=[
                ('is_active', models.BooleanField(default=True, verbose_name='Enable')),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('image', imagekit.models.fields.ProcessedImageField(upload_to=sso.api.res.models.upload_image)),
                ('name', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('location_at', models.CharField(blank=True, max_length=128, null=True)),
                ('taken_at', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('credit', models.CharField(blank=True, max_length=64, null=True)),
                ('credit_link', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
