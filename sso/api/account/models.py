from datetime import datetime, timedelta
import io
import re
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.images import ImageFile
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.utils.html import mark_safe
from hurry.filesize import size, verbose
from django.templatetags.static import static
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
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
        processors=[ResizeToFit(1920, 1080)],
        options={'quality': 85}, blank=True, null=True)
    created_at = models.DateTimeField('Dibuat pada', auto_now_add=True, help_text=__("Created at"))
    modified_at = models.DateTimeField('Diedit pada',auto_now=True, help_text=__("Modified at"))
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-full_name']
    
    def __str__(self):
        return self.email or self.eid

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
                self.password_last_change = datetime.now()
                if(not password_reset):
                    self.password_type = "USER"
        except:
            self.password_last_change = datetime.now()
        
        self.full_name = " ".join(list(map(lambda i: i.capitalize(),self.full_name.split(' '))))

        try:
            # FROM LDAP
            self.is_active = self._is_active == "active"
            if(self.password_type == None or self.password_type == ""):
                self.password_type = "USER"
            try:
                self.avatar = ImageFile(io.BytesIO(self._avatar), name='avatar.png')
            except:
                self.avatar = None
            pass
            print(self._groups)
        except:
            # MANUAL
            # LDAP().save_user(self)
            pass
        super(User, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # LDAPManager.deleteUser(self.email)
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
    now = datetime.now()
    start = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)  

