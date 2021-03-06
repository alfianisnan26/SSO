# Generated by Django 4.0.4 on 2022-06-11 03:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialOauthProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Enable')),
                ('provider', models.CharField(choices=[('facebook', 'Facebook'), ('google', 'Google'), ('twitter', 'Twitter')], max_length=16, unique=True)),
                ('key', models.CharField(max_length=512)),
                ('secret', models.CharField(max_length=512)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('order', models.SmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccountRegister',
            fields=[
                ('uuid', models.CharField(default=uuid.uuid4, editable=False, help_text='UUID', max_length=100, primary_key=True, serialize=False, unique=True, verbose_name='UUID')),
                ('uid', models.CharField(max_length=128, verbose_name='ID')),
                ('uname', models.CharField(blank=True, default='', max_length=128, null=True, verbose_name='Username or Email')),
                ('name', models.CharField(blank=True, default='', max_length=128, null=True, verbose_name='Name')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Enable')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auths.socialoauthprovider')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
