# Generated by Django 4.0.4 on 2022-07-04 17:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_remove_registrant_bypass'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagementAccount',
            fields=[
                ('uuid', models.CharField(default=uuid.uuid4, editable=False, help_text='Merupakan nomor yang terbentuk secara otomatis digunakan secara internal oleh sistem. Nomor ini ditetapkan sekali saat pengguna dibuat.', max_length=100, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Related User')),
            ],
        ),
    ]
