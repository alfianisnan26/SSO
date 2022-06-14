from uuid import uuid4
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
from sso.utils import parse_query_params

class ProviderManager:
    available = settings.SOCIAL_OAUTH2_PARAMETER

    def v(self, key):
        return self.available[self.obj.provider][key]

    def vp(provider):
        return ProviderManager.available[provider]

    def getSocialLoginContext(queries = None, reverser='social-login'):
        ctx = []
        q =  "" if queries == None else parse_query_params(queries, exclude=['state'], append={'do':'login'})
        
        for obj in SocialOauthProvider.objects.filter(is_active=True).order_by('order'):
            d = ProviderManager.vp(obj.provider)
            ctx.append({
                "name" : d['name'],
                "link" : reverse(reverser, kwargs={'provider':obj.provider}) + q,
                "slug" : obj.provider,
                "icon" : d['icon'],
                "color" : d['color'],
                "bg_color" : d['bg_color']
            })
        return ctx

    def __init__(self, request, provider, state='/', *args, **kwargs) -> None:
        self.request = request
        self.state = state
        self.provider = provider
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
        except:
            kwargs = {}

        h.fetch_token(  self.v('token_url'),
                        client_secret=self.obj.secret,
                        code = self.request.query_params["code"],
                        **kwargs)
        data = h.get(self.v('user_info_url')).json()
        
        if(self.provider == 'twitter'):
            data = data['data']
            print(data)
        

        out = {}
        for k,v in self.v('map').items():
            out[k] = data[v]
        
        return out

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

    uuid = models.CharField(max_length=100, default=uuid4, primary_key=True, unique=True, verbose_name='UUID', editable=False, help_text='UUID')
    uid = models.CharField(max_length=128, null=False,blank=False, verbose_name='ID')
    uname = models.CharField(max_length=128, null=True,blank=True, default="", verbose_name='Username or Email')
    name = models.CharField(max_length=128, null=True, blank=True, default="", verbose_name='Name')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="social")
    provider = models.ForeignKey(to=SocialOauthProvider, on_delete=models.CASCADE)

    registered_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField('Enable', default=True)
    def __str__(self) -> str:
        return self.user.username + ":" + self.provider.provider

    def regist(*args, **kwargs):
        user = get_object_or_404(User, uuid = kwargs.get('user'))
        data = ProviderManager(**kwargs).user_data()
        provider = SocialOauthProvider.objects.get(provider=kwargs.get('provider'))
        val = SocialAccountRegister(user=user, provider=provider, **data)
        if(SocialAccountRegister.objects.filter(provider=provider, uid=val.uid).exists()): raise Exception('conflict_with_other_account')
        return val

    def login(*args, **kwargs):
        data = ProviderManager(**kwargs).user_data()
        # TODO delete print data
        print(data)
        provider = SocialOauthProvider.objects.get(provider=kwargs.get('provider'), is_active=True)
        return SocialAccountRegister.objects.filter(provider=provider, uid=data['uid'])

    