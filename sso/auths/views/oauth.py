
from datetime import datetime, timedelta
import json
from django.http import HttpResponse
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
from oauth2_provider.models import Application
from sso import settings
from sso.api.account.utils import randStr
from oauth2_provider.models import Grant

@method_decorator(csrf_exempt, name="dispatch")
class TokenView(OAuthLibMixin, View):
    def create_token_response(self, request):
        if not hasattr(self, "_oauthlib_core") or oauth2_settings.ALWAYS_RELOAD_OAUTHLIB_CORE:
            server = self.get_server()
            core_class = self.get_oauthlib_backend_class()
            self._oauthlib_core = core_class(server)
        return self._oauthlib_core.create_token_response(request)

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        _, _, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
        return HttpResponse(content=body, status=status)

class GrantView(APIView):
    def get(self, request, app):
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