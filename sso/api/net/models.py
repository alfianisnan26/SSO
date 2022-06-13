from datetime import datetime
from uuid import uuid4
from django.db import models
import pytz
import routeros_api as r
from django.conf import settings

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
    profile = models.ForeignKey(to=Profile,verbose_name="Profil Jaringan",  on_delete=models.CASCADE, null=True, blank=True)
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


        ctx = r.RouterOsApiPool(
            host=settings.ROUTEROS_HOST.replace("https://",""),
            username=settings.ROUTEROS_API_USERNAME,
            password=settings.ROUTEROS_API_PASSWORD,
            use_ssl=True,
            plaintext_login=True
        )
        api = ctx.get_api()

        hotspot = api.get_resource('/ip/hotspot/user')
        users = hotspot.get(mac_address=self.mac)
        if(len(users) == 0):
            hotspot.add(
                name=self.uuid,
                mac_address=self.mac,
                limit_uptime="2m",
                limit_bytes_in="300",
                limit_bytes_out="400",
                email=self.user.email,
                profile="default",
                address=self.ip,
                password=self.token
            )
        # else:
        #     id = users[0]["id"]
        #     hotspot.set(id, name=self.uuid)
        #     hotspot.set(id, address=self.ip)
        #     hotspot.set(id, password=self.token)


        ctx.disconnect()
        self.save()