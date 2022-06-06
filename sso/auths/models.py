from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from sso.api.account.models import User

from django.conf import settings
from django.urls import reverse
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from sso.api.account.serializers import UserSerializer

class ProviderManager:
    available = {
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
                'code_challenge':'challenge',
                'code_challenge_method':'plain'
            },
            "optional_token_kwargs" : {
                'code_verifier':'challenge',
            },
            "map":{
                "uname":"email",
                "uid":"id",
                "name":"name"
            }
        }
    }

    def v(self, key):
        return self.available[self.obj.provider][key]

    def vp(provider):
        return ProviderManager.available[provider]

    def getSocialLoginContext(next):
        ctx = []
        for obj in SocialOauthProvider.objects.filter(is_active=True).order_by('order'):
            d = ProviderManager.vp(obj.provider)
            ctx.append({
                "name" : d['name'],
                "link" : reverse('social-login', kwargs={'provider':obj.provider}) + f"?do=login&next={next}",
                "slug" : obj.provider,
                "icon" : d['icon'],
                "color" : d['color'],
                "bg_color" : d['bg_color']
            })
        return ctx

    def __init__(self, request, provider, state='/', *args, **kwargs) -> None:
        self.request = request
        self.state = state
        self.obj = get_object_or_404(SocialOauthProvider, is_active=True, provider=provider)

    def redirect_uri(request:HttpRequest):
        url = request.build_absolute_uri(reverse("social-handler"))
        return url 

    def session(self) -> OAuth2Session:
        return OAuth2Session(self.obj.key,
                            state=self.state,
                            scope=self.v('scope'),
                            redirect_uri=ProviderManager.redirect_uri(self.request))
        
    def user_data(self):
        
        h = self.session()
        try:
            kwargs = self.v('optional_token_kwargs')
            print(kwargs)
        except:
            kwargs = {}

        h.fetch_token(  self.v('token_url'),
                        client_secret=self.obj.secret,
                        code = self.request.query_params["code"],
                        **kwargs)
        data = h.get(self.v('user_info_url'))
        return data.json()

    def redirect_authorize(self):
        try:
            kwarg = self.v('optional_auth_kwargs')
        except:
            kwarg = {}
        url, _ = self.session().authorization_url(self.v('auth_url'), **kwarg)
        return redirect(url)
    



class SocialOauthProvider(models.Model):
    available = list(map(lambda r: (r, ProviderManager.available[r]['name']), ProviderManager.available.keys()))

    is_active = models.BooleanField("Enable", default=True)
    provider = models.CharField(choices=available, unique=True, max_length=16)
    key = models.CharField(max_length=512, )
    secret = models.CharField(max_length=512)
    modified_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField(default=0)

    def __str__(self) -> str:
        try:
            return ProviderManager.available[self.provider]["name"]
        except:
            return "(unsupport)"

class SocialAccountRegister(models.Model):

    uid = models.CharField(max_length=128, null=False,blank=False, verbose_name='id')
    uname = models.CharField(max_length=128, null=True,blank=True, default="", verbose_name='Username or Email')
    name = models.CharField(max_length=128, null=True, blank=True, default="", verbose_name='Name')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="social")
    provider = models.ForeignKey(to=SocialOauthProvider, on_delete=models.CASCADE)

    registered_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField()

    def __str__(self) -> str:
        return self.user.username

    def regist(*args, **kwargs):
        user = get_object_or_404(User, uuid = kwargs.get('user'))
        data = ProviderManager(**kwargs).user_data()
        return {
            'user':UserSerializer(user).data,
            'data':data
        }

    def login(*args, **kwargs):
        data = ProviderManager(**kwargs).user_data()
        return data

    