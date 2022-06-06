from django.contrib import admin

from sso.api.res.models import Background

class BackgroundAdmin(admin.ModelAdmin):
    list_display=['thumbnail_tag', 'is_active', 'name','created_at', 'image']
    readonly_fields = ('image_tag', 'uuid')
    exclude = ['thumbnail_tag']
    list_editable = ['is_active']
    
admin.site.register(Background, BackgroundAdmin)