from django.contrib import admin

from sso.api.management.student.models import Generation, Group, PreviousSchool, Student

class GenerationAdmin(admin.ModelAdmin):
    list_display = ['__str__', "semester", "grade_info",  "name", "entry_year", "graduation_year", "is_graduated"]
    list_filter = ["semester", "is_graduated"]
    search_fields = ["name", "semester", "entry_year"]

class GroupAdmin(admin.ModelAdmin):
    list_display = ["__str__", "generation", "head_class_student", "homeroom_teacher", "name", "major", "group_number"]
    list_filter = ["major", "group_number", "generation__semester"]
    search_fields = ["name", "major", "group_number"]


class PreviousSchoolAdmin(admin.ModelAdmin):
    list_display = ["__str__", "address"]
    list_filter = ["type", "agency"]
    search_fields = ["name", "address"]

class StudentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "group"]
    list_filter = ["group__group_number", "group__major", "group__generation__semester"]
    search_fields = ["user", "group"]

admin.site.register(Generation, GenerationAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(PreviousSchool, PreviousSchoolAdmin)
admin.site.register(Student, StudentAdmin)