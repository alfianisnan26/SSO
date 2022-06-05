from django.contrib import messages
from django.utils.translation import ngettext
from django.contrib import admin
from sso.api.account.models import SocialMediaAccount, User
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
     actions = ['reset_password']
     @admin.action(description='Reset password to UUID or EID')
     def reset_password(self, request, queryset):
          for user in queryset:
               user.reset_password()
               user.save()

          self.message_user(request, ngettext(
               'a user password was reset to his UUID',
               f"{len(queryset)} user's passwords were reset to their UUID",
               len(queryset)
          ) + " or EID if available", messages.SUCCESS)
          
     
admin.site.register(User, UserAdmin)

class SocialMediaAccoutAdmin(admin.ModelAdmin):
     list_filter = ['provider', 'last_login']
     search_fields = ['user']
     list_display=['user','provider', 'uid', 'last_login', 'created_at', 'modified_at']
     readonly_fields = ['provider', 'uid', 'last_login', 'created_at', 'modified_at', 'uname', 'upic', 'name']

admin.site.register(SocialMediaAccount, SocialMediaAccoutAdmin)