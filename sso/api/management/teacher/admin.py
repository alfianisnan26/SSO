from django.contrib import admin

from sso.api.management.teacher.models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    pass

admin.site.register(Teacher, TeacherAdmin)