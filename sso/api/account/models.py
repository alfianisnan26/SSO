from datetime import date, datetime, timedelta
import io
import os
import re
import shutil
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.images import ImageFile
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit, SmartCrop
from django.utils.html import mark_safe
from hurry.filesize import size, verbose
from django.templatetags.static import static
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import pytz
from .variables import get as __
from sso.api.account.ldap import LDAP

from .managers import UserManager
from .utils import generate_password, upload_avatar

class User(AbstractBaseUser, PermissionsMixin):
    
    def generate_username(self):
        names = re.findall("[a-zA-Z]+", self.full_name)
        username = []
        for i in names:
            if(len(i) > 2):
                username.append(i.lower())
            if(len(username) >= 2):
                break
            
        username_base = ".".join(username)
        username = username_base
        loop = 2
        while User.objects.filter(Q(username=username) | Q(email=username + "@" + settings.MAIN_DOMAIN)).exists():
            username = username_base + str(loop)
            loop += 1
            
        return username

    def reset_password(self):
        self.password_last_change = datetime.now(tz=pytz.UTC)
        if(self.eid == None or self.eid == ""):
            self.password_type = "UUID"
            self.password = generate_password(self.uuid)
        else:
            self.password_type = "EID"
            self.password = generate_password(self.eid)
        return self.password

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    USER_TYPE = (
        ("STUDENT","Siswa"),
        ("GUEST","Tamu"),
        ("TEACHER","Guru"),
        ("STAFF","Staff"),
        ("ALUMNI","Alumni")
    )
    
    PASS_TYPE = [
        ("USER","User defined"),
        ("UUID","UUID Number"),
        ("EID", "ID Number")
    ]
    
    PERMISSION_TYPE = [
        ("yes", "Superuser"),
        ("staff", "Staff"),
        ("none", "Standar")
    ]
    
    
    objects = UserManager()
    is_active = models.BooleanField('Aktif', null=False, blank=False, default=True, help_text=__("Active"))
    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID', editable=False, help_text=__('UUID'))
    password = models.CharField(_("password"), max_length=128)
    password_last_change = models.DateTimeField('Perubahan kata sandi',null=True, blank=True, help_text=__("Password last change"))
    password_type = models.CharField('Jenis password tersetel', max_length=4, choices=PASS_TYPE,help_text=__("Password type"))
    full_name = models.CharField('Nama lengkap',max_length=70, default="")
    eid = models.CharField('NIS/NIP', unique=True, max_length=64, null=True, blank=True, help_text=__("EID"))
    username = models.CharField('Username', max_length=70, unique=True, blank=True, null=True, help_text=__("Username"))
    user_type = models.CharField('Peran pengguna',max_length=10, choices = USER_TYPE, null=True, default='GUEST')
    permission_type = models.CharField('Jenis pengguna', default='none', max_length=5, choices=PERMISSION_TYPE)
    email = models.EmailField(unique=True, help_text=__("Email"))
    phone = models.CharField('Telepon',max_length=16, blank=True, null=True,help_text=__("Phone"))
    avatar = ProcessedImageField(verbose_name='File foto',
        upload_to=upload_avatar,
        format='PNG',
        processors=[SmartCrop(600, 800)],
        options={'quality': 85}, blank=True, null=True)
    created_at = models.DateTimeField('Dibuat pada', auto_now_add=True, help_text=__("Created at"))
    modified_at = models.DateTimeField('Diedit pada',auto_now=True, help_text=__("Modified at"))
    USERNAME_FIELD = 'email'
    last_update = models.DateTimeField('Terakhir terlihat pada', null=True, blank=True)

    def is_online(self):
        try:
            return (self.last_update + timedelta(minutes=5)) > datetime.now(tz=pytz.UTC)
        except Exception as e:
            return False

    is_online.short_description = 'Online'

    def update(request):
        try:
            request.user.update_user()
        except Exception as e:
            pass

    def update_user(self, save=True):
        try:
            self.last_update = datetime.now(tz=pytz.UTC)
            if(save): self.save()
        except Exception as e:
            pass

    class Meta:
        ordering = ['-full_name']
    
    def __str__(self):
        return self.email or self.eid

    def set_password(self, raw_password):
        self.password = generate_password(raw_password)
        self._password = raw_password
        self.password_type = "USER"
        return self.password

    def check_password(self, raw_password):
        return LDAP().authenticate(self, raw_password)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if(self.permission_type == "yes"):
            self.is_superuser = True
            self.is_staff = True
            
        elif(self.permission_type == "staff"):
            self.is_superuser = False
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False
    
    def save(self, *args, **kwargs):

        if(hasattr(kwargs, 'request')):
            if(kwargs.get('request').user.id == self.id):
                self.update_user(save=False)
        try:
            self.password_last_change = datetime(1970,1,1,0,0) + timedelta(int(self._password_last_change))
            try:
                self.avatar = ImageFile(io.BytesIO(self._avatar), name=self.avatar.name)
            except:
                self.avatar = None

            self.is_active = self._is_active == "active"
        except Exception as e:
            pass
        if(not self.phone == None and self.phone[0] == "0"):
            self.phone = "+62" + self.phone[1:]

        if(self.username == None or self.username == ""):
            self.username = self.generate_username()

        if(self.email == None or self.email == ""):
            self.email = self.username + "@" + settings.MAIN_DOMAIN

        if(self.password == None or self.password == ""):
            password_reset = True
            self.reset_password()

        if('{SHA512}' in self.password):
            self.password = generate_password(self.password)

        try:
            user = User.objects.get(pk=self.pk)
            if((user.eid == None or user.eid == "") and not (self.eid == None or self.eid == "")):
                self.password = generate_password(self.password)
                self.password_type = "EID"
                
            if(self.password != user.password):
                self.password_last_change = datetime.now(tz=pytz.UTC)
                if(not password_reset):
                    self.password_type = "USER"
        except:
            self.password_last_change = datetime.now(tz=pytz.UTC)
        
        self.full_name = " ".join(list(map(lambda i: i.capitalize(),self.full_name.split(' '))))
        
        if(self.password_type == None or self.password_type == ""):
            self.password_type = "USER"
        super(User, self).save(*args, **kwargs)
        LDAP().update_user(self)

    def delete(self, *args, **kwargs):
        # print("DELETING USER")
        LDAP().delete_user(self)
        try:
            path = os.path.join(settings.MEDIA_ROOT, 'users', self.uuid)
            shutil.rmtree(path)
        except Exception as e:
            print(e)

        super(User, self).delete(*args, **kwargs)

    def thumbnail_tag(self):
        try:
            return mark_safe(f'<div style="width:100px;height:100px;"><img style="object-fit:cover;width:100%;height:100%;" src="{self.avatar.url}"/></div>')
        except:
            pass

    def image_tag(self):
        print(self.avatar.url)
        if(self.avatar == None):
            return self.email
        return mark_safe(f'<div style="width:200px;height:300px;"><img style="object-fit:cover;width:100%;height:100%;" src="{self.avatar.url}"/></div>')

    def get_avatar(self, placeholder:bool=False):
        try:
            return self.avatar.url
        except:
            if(placeholder):
                return static('assets/res/placeholder.png')

    image_tag.short_description = 'Photo'
    image_tag.allow_tags = True

    thumbnail_tag.short_description = 'Photo'
    thumbnail_tag.allow_tags = True
        

def default_start_time():
    now = datetime.now(tz=pytz.UTC)
    start = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)  

