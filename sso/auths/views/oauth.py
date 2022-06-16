
from datetime import datetime, timedelta
import json
from venv import create
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import pytz
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings
from oauthlib.oauth2.rfc6749.endpoints.pre_configured import Server
from oauthlib.common import Request
from oauth2_provider.models import Application, AccessToken, RefreshToken
from sso import settings
from sso.api.account.models import User
from sso.api.account.utils import randStr
from oauth2_provider.models import Grant
from passlib.hash import django_pbkdf2_sha256, sha256_crypt

@method_decorator(csrf_exempt, name="dispatch")
class TokenViewOauth(APIView):

    def create_token(self, user, application, N=255):
        for at in AccessToken.objects.filter(expires__lte = datetime.now(tz=pytz.UTC)):
            try:
                at.source_refresh_token.delete()
            except:
                pass

            try:
                at.delete()
            except:
                pass

        expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
        at = AccessToken(user=user, token=randStr(N=N), application=application, expires=expires, scope="read write")
        at.save()
        rt = RefreshToken(user=user, token=randStr(N=N), application=application, access_token=at)
        rt.save()
        at.source_refresh_token = rt
        at.save()
        return {
            "access_token" : at.token,
            "expires_in" : settings.TOKEN_EXPIRE_SECONDS,
            'token_type' : 'Bearer',
            'scope' : 'read write', 
            'refresh_token' : rt.token
        }

    def token_post_generator(self, request:HttpRequest):
        data = request.data
        try:
            app = Application.objects.get(client_id = data['client_id'])
            if(not django_pbkdf2_sha256.verify(data['client_secret'], app.client_secret)):
                return Response({'error':'Invalid user client secret'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error':'Perhaps aplication is not registered'}, status=status.HTTP_404_NOT_FOUND)

        if(data['grant_type'] == 'refresh_token'):
            try:
                token = RefreshToken.objects.get(token=data['refresh_token'], application=app)
                token.access_token.delete()
            except:
                return Response({'error':'refresh token is not valid, revoked, or expired'}, status=status.HTTP_404_NOT_FOUND)
            data = self.create_token(token.user, token.application)

            try:
                token.delete()
            except:
                pass
        
        elif(data['grant_type'] == 'authorization_code'):
            try:
                Grant.objects.filter(expires__lte = datetime.now(tz=pytz.UTC)).delete()
                grant = Grant.objects.get(code=data['code'], application=app)
            except:
                return Response({'error':'code not found. Perhaps it is invalid or expired'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                verifier = data['code_verifier']
            except:
                return Response({'error':'code_verifier must be supplied'}, status=status.HTTP_400_BAD_REQUEST)

            if(grant.code_challenge_method == 'plain'):
                if(not grant.code_challenge == verifier):
                    return Response({'error' : 'code challenge does not match'}, status=status.HTTP_400_BAD_REQUEST)
            elif(grant.code_challenge_method == 'S256'):
                # TODO : VERIFY PKCE
                # if(not sha256_crypt.verify(verifier, grant.code_challenge)):
                #    return Response({'error' : 'code challenge does not match'}, status=status.HTTP_400_BAD_REQUEST)
                pass
            data = self.create_token(grant.user, grant.application)
            grant.delete()
        else:
            return Response({"error":"grant type does not support"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)

    def post(self, request:HttpResponse):
        out = self.token_post_generator(request)
        # print(out.status_code, out.data)
        return out
        

class GrantView(APIView):
    def get(self, request:HttpRequest, app):
        User.update(request)
        try:
            app = get_object_or_404(Application, client_id = app)
            code = randStr(N=30)
            Grant(
                user = request.user,
                code = code,
                application = app,
                expires = datetime.now(tz=pytz.UTC) + timedelta(minutes=15),
                redirect_uri = app.redirect_uris.split(' ')[0],
                scope = 'read write',
                code_challenge = settings.APP_DEFAULT_CODE_CHALLENGE,
                code_challenge_method = settings.APP_DEFAULT_CODE_CHALLENGE_METHOD,
                claims = '{}'
            ).save()
            return redirect( app.redirect_uris.split(' ')[0] + "?code=" + code)
        except:
            return redirect(reverse('home') + "?state=error_access_denied")