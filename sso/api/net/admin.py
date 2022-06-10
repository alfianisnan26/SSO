from django.contrib import admin

from sso.api.net.models import Profile, Registrant

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'download_speed', 'upload_speed', 'download_quota', 'upload_quota', 'session_timeout']


class RegistrantAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile', 'mac', 'ip', 'last_login']
    exclude = ['uuid', 'token']
    readonly_fields = ['user_agent', 'uuid', 'token', 'last_login']



admin.site.register(Profile, ProfileAdmin)
admin.site.register(Registrant, RegistrantAdmin)