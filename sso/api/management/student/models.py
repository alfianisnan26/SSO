import math
from django.utils import timezone
from uuid import uuid4
from django.db import models
from sso.api.account.models import ManagementAccount
from django.utils.translation import gettext_lazy as _

from sso.api.management.teacher.models import Teacher

class Generation(models.Model): # Angkatan
    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID', editable=False, help_text=_('UUID'))
    semester = models.SmallIntegerField(default=1)
    entry_year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=64, null=True, blank=True)
    is_graduated = models.BooleanField(default=False)

    def generation(self):
        return self.entry_year - 1964

    def __str__(self):
        return _("Angkatan") + " " + str(self.generation())
    
    def graduation_year(self):
        return self.entry_year + 3
    
    def grade(self):
        return math.floor((self.semester + 1) / 2) + 9

    def grade_info(self):
        return str(self.grade())  + " - " +  (_("Genap") if(self.semester % 2 == 0) else _("Ganjil"))
    

class Group(models.Model): # Rombel
    AVAILABLE_MAJOR = [
        ("SCIENCE", _("MIPA")),
        ("SOCIAL", _("IIS")),
        ("LITERATURE", _("SASTRA"))
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID', editable=False, help_text=_('UUID'))
    major = models.CharField(verbose_name=_("Jurusan"), choices=AVAILABLE_MAJOR, max_length=10)
    group_number = models.SmallIntegerField(_("Rombel"))
    generation = models.ForeignKey(Generation, verbose_name=_("Angkatan"), on_delete=models.CASCADE)
    name = models.CharField(max_length=64, null=True, blank=True, verbose_name=_("Nama kelas"))
    homeroom_teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Wali Kelas"))
    head_class_student = models.ForeignKey('student.Student', verbose_name=_("Ketua Kelas"), null=True, blank=True, on_delete=models.SET_NULL,related_name="head_class")
    
    def __str__(self) -> str:
        major = "N/A"
        for i in Group.AVAILABLE_MAJOR:
            j, k = i
            if(self.major == j):
                major = k
        return f"{self.generation.grade()} {major} {self.group_number} ({self.generation.generation()})"
    

class PreviousSchool(models.Model):
    AVAILABLE_AGENCY = [
        ("STATE", "Negeri"),
        ("ABROAD", "Luar Negeri"),
        ("PRIVATE", "Swasta"),
    ]

    AVAILABLE_TYPE = [
        ("PESANTREN", "Pesantren"),
        ("BOARDING", "Boarding School"),
        ("FORMAL", "Formal"),
        ("PAKET", "Paket"),
    ]

    AVAILABLE_STAGE = [
        ("JHS", "SMP Sederajat"),
        ("SHS", "SMA Sederajat"),
        ("ES", "SD Sederajat"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID', editable=False, help_text=_('UUID'))
    name = models.CharField(max_length=128)
    agency = models.CharField(max_length=10, choices=AVAILABLE_AGENCY,null=True, blank=True)
    type = models.CharField(max_length=10, choices=AVAILABLE_TYPE,null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=128)
    stage = models.CharField(max_length=3, choices=AVAILABLE_STAGE,null=True, blank=True)

    def __str__(self):
        return self.name
    

class Student(ManagementAccount):
    group = models.ForeignKey(Group, verbose_name=_("Group"), on_delete=models.SET_NULL, null=True, blank=True)
    entry_date = models.DateField(default=timezone.now)
    previous_school_junior = models.ForeignKey(PreviousSchool, verbose_name=_("Previous School (Junior)"), on_delete=models.SET_NULL, null=True, blank=True, related_name="junior")
    previous_school_transfer = models.ForeignKey(PreviousSchool, verbose_name=_("Previous School (Transfer)"), on_delete=models.SET_NULL, null=True, blank=True, related_name="transfer")

    def __str__(self):
        return self.user.full_name