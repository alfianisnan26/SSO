from datetime import datetime
from uuid import uuid4
from django.db import models
import pytz

from sso.api.account.models import User
from sso.api.account.utils import randStr

class Profile(models.Model):
    name = models.CharField("Nama Profil",max_length=46)
    download_speed = models.IntegerField("Kecepatan Unduh")
    upload_speed = models.IntegerField("Kecepatan Unggah")
    download_quota = models.IntegerField("Kuota Unduh")
    upload_quota = models.IntegerField("Kuota Unggah")
    start_ip_address = models.CharField("Rentang Awal Alamat Hotspot", max_length=15)
    end_ip_address = models.CharField("Rentang Akhir Alamat Hotspot", max_length=15)
    keep_alive_timeout = models.DurationField("Waktu Tetap Terkoneksi")
    session_timeout = models.DurationField("Waktu Sesi")

    def __str__(self) -> str:
        return self.name

class Registrant(models.Model):
    user = models.ForeignKey(to=User,verbose_name="Pengguna", on_delete=models.CASCADE)
    profile = models.ForeignKey(to=Profile,verbose_name="Profil Jaringan",  on_delete=models.CASCADE)
    mac = models.CharField("Alamat MAC", unique=True, max_length=20)
    ip = models.CharField("Alamat IP", max_length=15)
    last_login = models.DateTimeField("Terakhir Masuk Pada", null=True, blank=True)
    token = models.CharField("Token", default=randStr, max_length=64)
    uuid = models.CharField("UUID", primary_key=True, default=uuid4, max_length=100)
    user_agent = models.CharField("Agen Pengguna", null=True, blank=True, max_length=128)
    bypass = models.BooleanField("Bypass Akses", default=False)

    def __str__(self) -> str:
        return self.user.username

    def login(self):
        self.last_login = datetime.now(tz=pytz.UTC)
        self.save()