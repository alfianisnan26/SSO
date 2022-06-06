from django.contrib import messages
from django.utils.translation import ngettext
from django.contrib import admin
from sso.api.account.models import User
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
     list_display=['username','is_active','full_name', 'last_login','thumbnail_tag','user_type','eid','email',  'created_at', 'modified_at', 'password_last_change', 'password_type','permission_type']
     exclude = ['user_permissions', 'is_superuser']
     readonly_fields = ('uuid','email','image_tag',  'last_login', 'created_at', 'modified_at', 'password_last_change', 'password_type','password')
     list_filter = ('is_active','user_type','permission_type','last_login', 'password_last_change','password_type', AvatarFilter,'groups')
     search_fields = ["email", "full_name", "username", 'eid']
     actions = ['reset_password', 'activate_user', 'deactivate_user', 'elevate_user','deelevate_user']
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

     


admin.site.register(User, UserAdmin)

