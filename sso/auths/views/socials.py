from django.http import HttpRequest
from django.shortcuts import redirect, render
from sso.auths.models import ProviderManager, SocialMediaAccount, SocialOauthProvider
from sso.auths.serializers import SocialMediaAccountSerializer
from sso.lang.lang import Str
from urllib.parse import urlencode, quote
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse_lazy
from rest_framework import views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.reverse import reverse
from requests_oauthlib import OAuth2Session
from requests_oauthlib import OAuth1
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import requests
from rest_framework_simplejwt.tokens import RefreshToken, Token
from twython import Twython
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_auth_ldap.backend import LDAPBackend           
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import HttpResponse 
from django.views.static import serve
from django.template.loader import render_to_string
import os

class OauthLogin(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request:HttpRequest, provider):
        state = request.META['QUERY_STRING'] + "&do=login" + "&provider=" + provider
        return ProviderManager(request, provider, state).redirect_authorize()
    
    def post(self, request:HttpRequest, provider):
        state = request.META['QUERY_STRING'] + "&do=register" + "&provider=" + provider + "&user=" + request.user.uuid
        return ProviderManager(request, provider, state).redirect_authorize()

class OauthCallback(views.APIView):
    def fetch_params(self, *args, **kwargs):
        for i in self.request.query_params["state"].split("&"):
            val = i.split("=")
            kwargs[val[0]] = val[1]
        return kwargs

    def get(self, request): 
        kwarg = self.fetch_params(request=request)  
        do = kwarg.get('do')
       
        if(do == "login"):
            SocialMediaAccount.login(**kwarg)
        elif(do == "register"):
            SocialMediaAccount.regist(**kwarg)

        return Response()