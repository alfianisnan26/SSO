"""
Django settings for sso project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import datetime
from pathlib import Path
import os
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType, LDAPSearchUnion, GroupOfNamesType, ActiveDirectoryGroupType

# Generating django environment
import environ

env = environ.Env()

# reading .env file
environ.Env.read_env()

MAIN_DOMAIN = env('MAIN_DOMAIN')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG") == "True"

ALLOWED_HOSTS = env('HOST').split(';')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd parties apps
    'corsheaders',
    'rest_framework',
    'sslserver',
    'oauth2_provider',
    'imagekit',

    # Internal apps
    'sso.api.account',
    'sso.api.res',
    'sso.auths',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    
    # CORS Middleware
    'corsheaders.middleware.CorsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



# CORS Header Setting
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'sso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "sso/resources/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sso.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASS"),
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'id'

from django.utils.translation import gettext_lazy as _

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT  = os.path.join(BASE_DIR, 'sso', 'resources','static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'sso', 'resources','static'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'sso', 'resources', 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    "django_auth_ldap.backend.LDAPBackend",
    'oauth2_provider.backends.OAuth2Backend',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')

# SOCIAL CONFIGURATION

SOCIAL_AUTH_GOOGLE_KEY = env("GOOGLE_KEY")
SOCIAL_AUTH_GOOGLE_SECRET = env("GOOGLE_SECRET")

SOCIAL_AUTH_FACEBOOK_KEY = env("FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = env("FACEBOOK_SECRET")

SOCIAL_AUTH_TWITTER_KEY = env("TWITTER_KEY")
SOCIAL_AUTH_TWITTER_SECRET = env("TWITTER_SECRET")

SOCIAL_OAUTH2_PARAMETER = {
    "facebook": {
        'name' : "Facebook",
        'scope': ['email','public_profile','user_photos','user_link','user_birthday'],
        'token_url' : 'https://graph.facebook.com/oauth/access_token',
        'user_info_url' : 'https://graph.facebook.com/v12.0/me?fields=id,name,picture,email',
        'auth_url' : 'https://www.facebook.com/dialog/oauth',
        "icon" : '/static/assets/icons/fb.png',
        "color": "white",
        "bg_color": "#3b5998",
        "map":{
            "uname":"email",
            "uid":"id",
            "name":"name"
        }
        
    },
    "google" : {
        'name' : 'Google',
        'scope' : ['openid','https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile',],
        'token_url' : "https://www.googleapis.com/oauth2/v4/token",
        'user_info_url' : "https://www.googleapis.com/oauth2/v1/userinfo",
        'auth_url' : "https://accounts.google.com/o/oauth2/v2/auth",
        "icon" : "/static/assets/icons/gg.png",
        "color": "black",
        "bg_color": "white",
        "map":{
            "uname":"email",
            "uid":"id",
            "name":"name"
        }
    },
    "twitter" : {
        "name" : "Twitter",
        'scope' : ['tweet.read', 'users.read'],
        'token_url' : 'https://api.twitter.com/2/oauth2/token',
        "user_info_url" : "https://api.twitter.com/2/users/me",
        "auth_url" : "https://twitter.com/i/oauth2/authorize",
        "icon" : '/static/assets/icons/tw.png',
        "color": "white",
        "bg_color": "#1DA1F2",
        "optional_auth_kwargs" : {
            'code_challenge':'r9gBkX2uP0Ztubf0pmGCtAEJ2r-tCBTDkbJyQKfKvDU',
            'code_challenge_method':'S256'
        },
        "optional_token_kwargs" : {
            'code_verifier':'gmz4ZMFJL7yyYowvSGNqzjxUXTvj0up00vhTwg-sbERcfYIoSdifqXY6_ASOAQ2mbe197mbuVg-3PMYrqgMHaKbrtGMGjJARQTCVicED0O53W-NqjM7z_XsQi8UgdaKo',
        },
        "map":{
            "uname":"username",
            "uid":"id",
            "name":"name"
        }
    }
}

# LDAP Configuration

DOMAIN_NAME = ",".join(list(map(lambda r: "dc=" + r, str(MAIN_DOMAIN).split("."))))
AUTH_LDAP_SERVER_URI = "ldap://localhost"
AUTH_USER_MODEL = 'account.User'

AUTH_LDAP_BIND_DN = "cn=Manager," + DOMAIN_NAME
AUTH_LDAP_PASSWORD = env("LDAP_PASSWORD")
LDAP_BASEDN = 'o=domains,' + DOMAIN_NAME 

AUTH_LDAP_USER_DN_TEMPLATE = "mail=%(user)s,ou=Users,domainName=" + MAIN_DOMAIN + "," + LDAP_BASEDN

AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sn",
    "full_name": "cn",
    "email":"mail",
    "password":"userPassword",
    "user_type":"employeeType",
    "phone":"mobile",
    "eid":"employeeNumber",
    "permission_type":"domainGlobalAdmin",
    "_avatar":"jpegPhoto",
    "_is_active" : "accountStatus",
    "_password_last_change" : "shadowLastChange"
    }

# AUTH_LDAP_PROFILE_ATTR_MAP = {
#     "home_directory": "homeDirectory"
# }

AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_CACHE_TIMEOUT = 3600
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

# AUTH_LDAP_FIND_GROUP_PERMS = True
# AUTH_LDAP_MIRROR_GROUPS = True

# AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
# AUTH_LDAP_GROUP_TYPE = PosixGroupType(name_attr ="cn")
# AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
# AUTH_LDAP_GROUP_SEARCH =

DEFAULT_EMAIL_QUOTA = "524288"

# OAUTH
PKCE_REQUIRED = True
AUTHORIZATION_CODE_EXPIRE_SECONDS = 3600
TOKEN_EXPIRE_SECONDS = 3600
LOGIN_URL = "/login/?state=alert_must_login"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken" 

EMAIL_DEFAULT_CLIENT_ID = 'FXBPpK0ZFNCO945Drpd8NPNGelB0TsH61YN8q8Wt'
EMAIL_DEFAULT_CLIENT_SECRET = 'WANzFbl6D6NeLkrT6r7EfDiuCaCYSsSQx9kHRmvZzUAlJmwd1oy6SLkfBkn3Dl0SSHUs4lrURWvxCVEK5kAoXBZEkW2Xg4e42YpnvVcLYquRMExgtlCuivhw9zANrIzU'

APP_DEFAULT_CLIENT_ID = 'KUTzfO01UytGthkjLotBCESGXOy11UVG9Iez0vWX'
APP_DEFAULT_CLIENT_SECRET = '6nerHP14Z2NopMgRtOpaFbDr44m5bzNE1gsd23YQaN1YMrMspgLO2pzOYCJPmTqWCv616u7qsDhngU9atYshV37H7QFfqVMcDGN3ur1YprKACBwBgK6r6B52fnBGtoHH'

APP_DEFAULT_CODE_CHALLENGE = "oXl13aZf2yJDDue6hoCetYar4u8d7FymtUmHJfLq6Eo"
APP_DEFAULT_CODE_CHALLENGE_METHOD = "S256"