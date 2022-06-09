from datetime import datetime
from django.http import HttpRequest
from django.shortcuts import redirect
from rest_framework import status
import pytz
from sso.api.account.models import User
from sso.api.serializers import SocialAccountRegisterSerializer
from sso.auths.models import ProviderManager, SocialAccountRegister, SocialOauthProvider
from django.conf import settings
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.contrib.auth import login
from rest_framework import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class OauthLogin(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request:HttpRequest, provider):
        state = request.META['QUERY_STRING'] + "&do=login" + "&provider=" + provider
        return ProviderManager(request, provider, state).redirect_authorize()

class OauthRegister(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request:HttpRequest, provider):
        User.update(request)
        state = request.META['QUERY_STRING'] + "&do=register" + "&provider=" + provider + "&user=" + request.user.uuid
        return ProviderManager(request, provider, state).redirect_authorize()

class OauthCallback(views.APIView):
    def fetch_state(request):
        kwargs = {'request': request}
        params = request.query_params["state"].split("&")
        print(params)
        for i in [var for var in params if var]:
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
            if(not request.user.is_authenticated):
                return Response(status=status.HTTP_403_FORBIDDEN)
            try:
                data = SocialAccountRegister.regist(**state)
                data.save()
                data = SocialAccountRegisterSerializer(data).data
            except Exception as e:
                print('ERROR : ', e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
                
        if(hasattr(state, 'next')):
            return redirect(state.get('next'))

        return Response(data=data)