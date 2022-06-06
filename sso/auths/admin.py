from django import forms
from django.db import models
from django.contrib import admin
from django.contrib import messages
from sso.auths.models import ProviderManager, SocialAccountRegister, SocialOauthProvider

class KeySecretAdminForm(forms.ModelForm):
    def redirect_uri(self, request):
        return 'data'

class SocialOauthProviderAdmin(admin.ModelAdmin):
    # exclude = ['key', 'secret']
    list_display = ['provider', 'is_active','order','modified_at']
    ordering = ('order',)
    list_editable = ['is_active', 'order']
    form = KeySecretAdminForm
    # readonly_fields = ['redirect_uri',]
    

    def save_model(self, request, obj, form, change) -> None:
        # obj.key = form.cleaned_data['key_form']
        # obj.secret = form.cleaned_data['secret_form']
        messages.add_message(request, messages.INFO, 'Pastikan redirect uri pada Admin Console ' + ProviderManager.vp(obj.provider)['name'] + ' telah di set menjadi ' + ProviderManager.redirect_uri(request))
        return super().save_model(request, obj, form, change)

admin.site.register(SocialOauthProvider, SocialOauthProviderAdmin)

class SocialMediaAccoutAdmin(admin.ModelAdmin):
    # def has_add_permission(self, request):
    #     return False

    
    list_filter = ['provider', 'is_active', 'last_login', 'registered_at']
    search_fields = ['name','uname','id', 'provider__provider', 'user__full_name']
    list_display=['user','provider','is_active', 'uid', 'last_login', 'registered_at']
    readonly_fields = ['last_login', 'registered_at']
    # TODO SET TO READ ONLY
    # def get_readonly_fields(self, request, obj=None):
    #     return list(set(
    #         [field.name for field in self.opts.local_fields] +
    #         [field.name for field in self.opts.local_many_to_many]
    #     ))

admin.site.register(SocialAccountRegister, SocialMediaAccoutAdmin)