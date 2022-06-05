import json
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
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
# Server.create_token_response

@method_decorator(csrf_exempt, name="dispatch")
class TokenView(OAuthLibMixin, View):

    def create_token_response(self, request):

        if not hasattr(self, "_oauthlib_core") or oauth2_settings.ALWAYS_RELOAD_OAUTHLIB_CORE:
            server = self.get_server()
            core_class = self.get_oauthlib_backend_class()
            self._oauthlib_core = core_class(server)
        
        core:OAuthLibCore = self._oauthlib_core
        server:Server = core.server

        ep = core._extract_params(request)
        ec = core._get_extra_credentials(request)
        uri, http_method, body, headers = ep
        
        out = server.create_token_response(uri=uri, http_method=http_method, body=body, headers=headers, credentials = ec)

        # request = Request(uri, http_method=http_method, body=body, headers=headers)
        # # print("Request : ", request)
        # # out = server.validate_token_request(request)

        # # print("Output : ", out)

        return self._oauthlib_core.create_token_response(request)

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        for i in sorted(request.META):
            print(i, request.META[i])
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
        print(status, body)
        response = HttpResponse(content=body, status=status)
        return response