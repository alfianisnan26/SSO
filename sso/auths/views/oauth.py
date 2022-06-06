from audioop import reverse
import json
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.mixins import OAuthLibMixin
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.views import AuthorizationView as AuthorizationViewTemplate
from oauthlib.oauth2.rfc6749.endpoints.pre_configured import Server
from oauthlib.common import Request
from oauth2_provider.models import Application
# Server.create_token_response

class AuthorizationView(AuthorizationViewTemplate):
    pass
    # def get(self, request, *args, **kwargs):
    #     data = super().get(request, *args, **kwargs)
    #     print(data.__dict__)
    #     return data
    # def get(self, request, *args, **kwargs):
    #     if(request.user.is_authenticated):
    #         try:
    #             data:dict = request.query_params
    #             if(not data['response_type'] == 'code'):
    #                 raise Exception('response_type is not support')
    #             obj = Application.objects.get(
    #                 client_id=data['client_id'],
    #                 redirect_uris=data['redirect_uri'],
    #             )
    #             return Response(
    #                 {'data':data,
    #                 'app':obj.name},
    #                 status=status.HTTP_302_FOUND)
    #         except Exception as e:
    #             return Response({"detail":str(e)},status.HTTP_400_BAD_REQUEST)
    #     else:
    #         redirect(reverse('login') + '?next=' + reverse('authorize'))

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
        