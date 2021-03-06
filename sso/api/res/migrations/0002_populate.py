# Generated by Django 4.0.4 on 2022-06-06 05:06

import io
from unicodedata import name
from django.conf import settings
from django.db import migrations
from sso.api.res.models import Background
from django.core.files.images import ImageFile
import os
class Migration(migrations.Migration):

    def populate(*args, **kwargs):
        dir = os.path.join(settings.STATICFILES_DIRS[0], 'assets', 'img')
        for i in os.listdir(dir):
            file = open(os.path.join(dir, i), 'rb')
            bg = Background(
                image=ImageFile(io.BytesIO(file.read()), name=i),
                description='(Auto-generated)',
                name=i)
            bg.save()

    def reverse(*args, **kwargs):
        Background.objects.filter(description__icontains='(Auto-generated)').delete()

    dependencies = [
        ('res', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate, reverse)
    ]
