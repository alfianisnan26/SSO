from sso.api.account.serializers import UserPublicSerializer
from sso.auths.models import SocialAccountRegister, SocialOauthProvider
from rest_framework import serializers


class SocialAccountRegisterSerializer(serializers.ModelSerializer):
    # user = UserPublicSerializer()
    provider = serializers.SerializerMethodField()

    def get_provider(self, obj):
        return obj.provider.provider
        
    class Meta:
        model = SocialAccountRegister
        fields = ['uuid','provider','name', 'uname','uid',]