from datetime import datetime
from django.http import HttpRequest
from django.shortcuts import redirect, render
import pytz
from sso.auths.models import ProviderManager, SocialAccountRegister, SocialOauthProvider
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
from django.contrib.auth import login

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
    def fetch_state(request):
        kwargs = {'request': request}
        for i in request.query_params["state"].split("&"):
            j = i.split("=")
            kwargs[j[0]] = j[1]
        return kwargs

    def get(self, request): 
        state:dict = OauthCallback.fetch_state(request) 
        do = state.get('do')
        data = {}
        error = request.query_params.get('error')
        if(error != None):
            return redirect(reverse('login') + f"?state=error_{error}&next={state.get('next')}")
        if(do == "login"):
            try:
                obj = SocialAccountRegister.login(**state)
                if(obj.exists()):
                    obj:SocialAccountRegister = obj.first()
                    obj.last_login = datetime.now(tz=pytz.UTC)
                    obj.save()
                    login(request, obj.user, backend=settings.AUTHENTICATION_BACKENDS[0])
                    return redirect(reverse('home') + f"?next={state.get('next')}")
                else:
                    return redirect(reverse('login') + f"?state=error_msyacw&next={state.get('next')}")
            except Exception as e:
                print(e)
                return redirect(reverse('login') + f"?state=error_clwsa&next={state.get('next')}")
        elif(do == "register"):
            data = SocialAccountRegister.regist(**state)
    
        return Response(data=data)