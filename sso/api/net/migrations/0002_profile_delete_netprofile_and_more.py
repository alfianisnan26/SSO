# Generated by Django 4.0.4 on 2022-06-10 17:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('net', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=46, verbose_name='Nama Profil')),
                ('download_speed', models.IntegerField(verbose_name='Kecepatan Unduh')),
                ('upload_speed', models.IntegerField(verbose_name='Kecepatan Unggah')),
                ('download_quota', models.IntegerField(verbose_name='Kuota Unduh')),
                ('upload_quota', models.IntegerField(verbose_name='Kuota Unggah')),
                ('start_ip_address', models.CharField(max_length=15, verbose_name='Rentang Awal Alamat Hotspot')),
                ('end_ip_address', models.CharField(max_length=15, verbose_name='Rentang Akhir Alamat Hotspot')),
                ('keep_alive_timeout', models.DurationField(verbose_name='Waktu Tetap Terkoneksi')),
                ('session_timeout', models.DurationField(verbose_name='Waktu Sesi')),
            ],
        ),
        migrations.DeleteModel(
            name='NetProfile',
        ),
        migrations.RenameModel(
            old_name='NetRegistrant',
            new_name='Registrant',
        ),
        migrations.AlterField(
            model_name='registrant',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='net', to='net.profile', verbose_name='Profil Jaringan'),
        ),
    ]