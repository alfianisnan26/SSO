from pyexpat import model
import warnings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from importlib import import_module
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

from sso.auths.models import SocialAccountRegister