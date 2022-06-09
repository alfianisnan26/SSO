from django.http import HttpRequest
from django.shortcuts import redirect
from sso.api.account.models import User
from sso.api.serializers import SocialAccountRegisterSerializer
from sso.auths.models import SocialAccountRegister, SocialOauthProvider
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login
from rest_framework import views

from sso.permissions import ReadOnly

class AvailableSocialProvider(views.APIView):
    permission_classes = [ReadOnly]
    def get(self, request:HttpRequest, *args, **kwargs):
        User.update(request)
        objs = SocialOauthProvider.objects.filter(is_active=True)
        data = {}
        for i in objs:
            data[i.provider] = {
                'login' : request.build_absolute_uri(reverse('social-login', kwargs={'provider': i.provider})),
                'register' : request.build_absolute_uri(reverse('social-register', kwargs={'provider': i.provider}))
            }
        return Response(data)

class SocialOauthRegisterMe(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request:HttpRequest, *args, **kwargs):
        User.update(request)
        regs = SocialAccountRegister.objects.filter(user=request.user)
        objs = SocialOauthProvider.objects.filter(is_active=True)
        data = {}
        for i in objs:
            data[i.provider] = {
                'get' : request.build_absolute_uri(reverse('social-login', kwargs={'provider': i.provider})),
                'post' : request.build_absolute_uri(reverse('social-register', kwargs={'provider': i.provider}))
            }
        
        registered = SocialAccountRegisterSerializer(regs, many=True).data

        for i in regs:
            provider = i.provider.provider
            if(provider in data.keys()):
                data[provider] = {'delete' : request.build_absolute_uri(reverse('social-login', kwargs={'provider': i.provider})),}

        return Response({
            'available' : data,
            'registered' : registered,
        })