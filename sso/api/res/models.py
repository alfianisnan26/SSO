from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from django.utils.html import mark_safe
from hurry.filesize import size, verbose
from uuid import uuid4
import os

def upload_image(instance, filename):
    return os.path.join('res', 'bg', str(instance.uuid) + '.webp')

class Background(models.Model):
    is_active = models.BooleanField('Enable', default=True)
    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID')
    image = ProcessedImageField(
        upload_to=upload_image,
        format='WEBP',
        processors=[ResizeToFit(800, 800)],
        options={'quality': 75}, blank=False, null=False)
    name = models.CharField(max_length=64, blank=True, null=True, default="")
    location_at = models.CharField(max_length=128, blank=True, null=True)
    taken_at = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    credit = models.CharField(max_length=64, blank=True, null=True)
    credit_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if(self.name == ""):
            return self.uuid
        return self.name
    

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="500" height="auto" />'
        f'<p>{self.image.width} x {self.image.height} pixels<br>({size(self.image.size, system=verbose)})</p>')
    
    def thumbnail_tag(self):
        return mark_safe(f'<div style="width:100px;height:100px;"><img style="object-fit:cover;width:100%;height:100%;" src="{self.image.url}"/></div>')

    image_tag.short_description = 'Preview'
    image_tag.allow_tags = True

    thumbnail_tag.short_description = 'Image'
    thumbnail_tag.allow_tags = True

    def save(self, *args, **kwargs):
        super(Background, self).save(*args, **kwargs)
