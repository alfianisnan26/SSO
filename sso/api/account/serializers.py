from datetime import datetime, timedelta
from django.http import HttpRequest
import pytz
from rest_framework import serializers
from sso.api.account.models import User

class UserSerializer(serializers.ModelSerializer):

    is_online = serializers.SerializerMethodField()
    def get_is_online(self, obj):
        try:
            return (obj.last_update + timedelta(minutes=5)) > datetime.now(tz=pytz.UTC)
        except Exception as e:
            return False

    class Meta:
        model = User
        exclude = [
            'is_superuser',
            'password'
        ]


class UserMinimalSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    def get_is_online(self, obj):
        try:
            return (obj.last_update + timedelta(minutes=5)) > datetime.now(tz=pytz.UTC)
        except Exception as e:
            return False
            

    class Meta:
        model = User
        fields = ['uuid', 'last_login', 'full_name', 'eid', 'username', 'email', 'profile', 'avatar', 'is_online']

class UserPublicSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    def get_is_online(self, obj):
        try:
            return (obj.last_update + timedelta(minutes=5)) > datetime.now(tz=pytz.UTC)
        except Exception as e:
            return False
            
            
    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'is_online', 'avatar']