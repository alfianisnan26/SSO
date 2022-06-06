from rest_framework.serializers import Serializer

from sso.api.account.models import User
class UserSerializer(Serializer):
    class Meta:
        model = User
        fields = '__all__'