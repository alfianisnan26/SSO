
from datetime import datetime, timedelta
import json
from venv import create
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.utils.decorators import method_decorator
import pytz
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.mixins import OAuthLibMixin
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.settings import oauth2_settings
from oauthlib.oauth2.rfc6749.endpoints.pre_configured import Server
from oauthlib.common import Request
from oauth2_provider.models import Application, AccessToken, RefreshToken
from sso import settings
from sso.api.account.utils import randStr
from oauth2_provider.models import Grant
from passlib.hash import django_pbkdf2_sha256, sha256_crypt

# @method_decorator(csrf_exempt, name="dispatch")
# class TokenView(OAuthLibMixin, View):
#     def create_token_response(self, request):
#         print(request.body)
#         if not hasattr(self, "_oauthlib_core") or oauth2_settings.ALWAYS_RELOAD_OAUTHLIB_CORE:
#             server = self.get_server()
#             core_class = self.get_oauthlib_backend_class()
#             self._oauthlib_core = core_class(server)
#         return self._oauthlib_core.create_token_response(request)

#     @method_decorator(sensitive_post_parameters("password"))
#     def post(self, request, *args, **kwargs):
#         _, _, body, status = self.create_token_response(request)
#         if status == 200:
#             access_token = json.loads(body).get("access_token")
#             if access_token is not None:
#                 token = get_access_token_model().objects.get(token=access_token)
#                 app_authorized.send(sender=self, request=request, token=token)
#         print("On Token post request")
#         print(body)
#         return HttpResponse(content=body, status=status)
# {'code': ['JSTiLhnMHBICv8sec40uKCto9BsqWn'], 'client_id': ['FXBPpK0ZFNCO945Drpd8NPNGelB0TsH61YN8q8Wt'], 'client_secret': ['WANzFbl6D6NeLkrT6r7EfDiuCaCYSsSQx9kHRmvZzUAlJmwd1oy6SLkfBkn3Dl0SSHUs4lrURWvxCVEK5kAoXBZEkW2Xg4e42YpnvVcLYquRMExgtlCuivhw9zANrIzU'], 'redirect_uri': ['https://mail.smandak.sch.id/index.php/login/oauth'], 'grant_type': ['authorization_code'], 'code_verifier': ['gmz4ZMFJL7yyYowvSGNqzjxUXTvj0up00vhTwg-sbERcfYIoSdifqXY6_ASOAQ2mbe197mbuVg-3PMYrqgMHaKbrtGMGjJARQTCVicED0O53W-NqjM7z_XsQi8UgdaKo']}
# {"access_token": "Q9Ze5clRZPfIWVEdzRY7JidZpCzW7g", "expires_in": 36000, "token_type": "Bearer", "scope": "read write", "refresh_token": "zmA1IlpX26aRYgthvqmIsho2PeOGls"}
@method_decorator(csrf_exempt, name="dispatch")
class TokenViewOauth(APIView):

    def create_token(self, user, application):
        expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
        at = AccessToken(user=user, token=randStr(N=30), application=application, expires=expires, scope="read write")
        at.save()
        rt = RefreshToken(user=user, token=randStr(N=30), application=application, access_token=at)
        rt.save()
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
                return Response({'error':'[Application] Invalid user client secret'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({'error':'Perhaps aplication is not registered'}, status=status.HTTP_404_NOT_FOUND)

        if(data['grant_type'] == 'refresh_token'):
            try:
                token = RefreshToken.objects.get(token=data['refresh_token'], application=app)
            except:
                return Response({'error':'refresh token is not valid, revoked, or expired'}, status=status.HTTP_404_NOT_FOUND)
            data = self.create_token(token.user, token.application)
        elif(data['grant_type'] == 'authorization_code'):
            try:
                grant = Grant.objects.get(code=data['code'], expires__gte = datetime.now(tz=pytz.UTC), application=app)
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
        else:
            return Response({"error":"grant type does not support"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)

    def post(self, request:HttpResponse):
            out = self.token_post_generator(request)
            print(out.status_code, out.data)
            return out
        

class GrantView(APIView):
    def get(self, request:HttpRequest, app):
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