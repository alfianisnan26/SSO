from dataclasses import field
from django.contrib import messages
from django.utils.translation import ngettext
from django.contrib import admin
from django import forms
from sso.api.account.models import Profile, Registrant, User
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
class AvatarFilter(SimpleListFilter):
     title = _('ketersediaan foto')
     parameter_name = 'avatar'
     
     def lookups(self, request, model_admin):
          return  [('T', _('Dengan foto')),('F', _('Tanpa foto'))]

     def queryset(self, request, queryset):
          if(self.value() == 'T'):
               return queryset.exclude(avatar="")
          elif(self.value() == 'F'):
               return queryset.filter(avatar="")
          else:
               return queryset


class UserAdmin(admin.ModelAdmin):
     list_display=['username','is_active','full_name', 'last_login','thumbnail_tag','profile','eid','email', 'is_online','last_update', 'created_at', 'modified_at', 'password_last_change', 'password_type','permission_type']
     exclude = ['user_permissions', 'is_superuser', 'password']
     readonly_fields = ('uuid','email','image_tag',  'last_login', 'is_online','last_update', 'created_at', 'modified_at', 'password_last_change', 'password_type')
     list_filter = ('is_active','profile','permission_type','last_login', 'password_last_change','password_type', AvatarFilter,'groups')
     search_fields = ["email", "full_name", "username", 'eid']
     actions = ['reset_password', 'activate_user', 'deactivate_user', 'elevate_user','deelevate_user']
     list_editable = ['is_active', 'profile']
     
     @admin.action(description='Reset password')
     def reset_password(self, request, queryset):
          for user in queryset:
               user.reset_password()
               user.save()
          self.message_user(request, f'{len(queryset)} password akun pengguna telah direset. Lihat bagian Jenis Password Disetel', messages.SUCCESS)

     @admin.action(description='Aktifkan pengguna')
     def activate_user(self, request, queryset):
          queryset.update(is_active=True)
          self.message_user(request, f'{len(queryset)} pengguna diaktifkan', messages.SUCCESS)
          
     @admin.action(description='Matikan pengguna')
     def deactivate_user(self, request, queryset):
          queryset.update(is_active=False)
          self.message_user(request, f'{len(queryset)} pengguna dimatikan', messages.SUCCESS)

     @admin.action(description='Tingkatkan pengguna menjadi staff')
     def elevate_user(self, request, queryset):
          queryset.update(permission_status='staff')
          self.message_user(request, f'{len(queryset)} pengguna ditingkatkan menjadi staff', messages.SUCCESS)
     
     @admin.action(description='Kembalian pengguna menjadi standar')
     def deelevate_user(self, request, queryset):
          queryset.update(permission_status='none')
          self.message_user(request, f'{len(queryset)} pengguna dikembalikan menjadi standar', messages.SUCCESS)

     # @admin.action(description='Ubah pengguna menjadi Siswa')
     # def user_to_student(self, request, queryset):
     #      queryset.update(profile='STUDENT')
     #      self.message_user(request, f'{len(queryset)} pengguna di ubah ke Siswa', messages.SUCCESS)

     # @admin.action(description='Ubah pengguna menjadi Staff')
     # def user_to_staff(self, request, queryset):
     #      queryset.update(profile='STAFF')
     #      self.message_user(request, f'{len(queryset)} pengguna di ubah ke Staff', messages.SUCCESS)

     # @admin.action(description='Ubah pengguna menjadi Guru')
     # def user_to_teacher(self, request, queryset):
     #      queryset.update(profile='TEACHER')
     #      self.message_user(request, f'{len(queryset)} pengguna di ubah ke Guru', messages.SUCCESS)

     # @admin.action(description='Ubah pengguna menjadi Alumni')
     # def user_to_alumni(self, request, queryset):
     #      queryset.update(profile='ALUMNI')
     #      self.message_user(request, f'{len(queryset)} pengguna di ubah ke Alumni', messages.SUCCESS)

     # @admin.action(description='Ubah pengguna menjadi Tamu')
     # def user_to_guest(self, request, queryset):
     #      queryset.update(profile='GUEST')
     #      self.message_user(request, f'{len(queryset)} pengguna di ubah ke Tamu', messages.SUCCESS)

     def delete_queryset(self, request, queryset):
          for i in queryset:
               i.delete()
          
     
class ProfileAdmin(admin.ModelAdmin):
     list_display = ['name', 'shared_user', 'download_speed', 'upload_speed', 'download_quota', 'upload_quota']
     

class RegistrantAdmin(admin.ModelAdmin):
     list_display = ['user', 'last_login']
     readonly_fields = ['token', 'uuid', 'last_login']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Registrant, RegistrantAdmin)

