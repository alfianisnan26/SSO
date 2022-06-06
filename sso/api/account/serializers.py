from django.http import HttpRequest
from rest_framework import serializers
from sso.api.account.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            'is_superuser',
            'password'
        ]


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'last_login', 'full_name', 'is_active', 'eid', 'username', 'user_type', 'avatar']