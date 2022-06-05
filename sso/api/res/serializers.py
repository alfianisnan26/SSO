from rest_framework import serializers

from sso.api.res.models import Background

class BackroundSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Background
        fields = "__all__"

    def get_image(self, obj):
        return obj.image.url
