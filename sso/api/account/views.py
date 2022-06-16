import django
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from sso.api.account.models import User
from sso.api.account.serializers import UserSerializer
from sso.auths.models import ProviderManager, SocialAccountRegister
from sso.auths.utils import Toast
from sso.lang.lang import Str
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.images import ImageFile

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        User.update(request)
        serializer = UserSerializer(request.user).data
        return Response(serializer)

    def post(self, request):
        User.update(request)
        pass

    def delete(self, request):
        User.update(request)
        pass

class Dashboard(View):
    def get(self, request):
        toasts = Toast()

        try:
            state = request.GET["state"]
            toasts.create(f"str:{state}", type=state.split("_")[0].upper(), timeout=5)
        except Exception as e:
            pass
        
        logins = ProviderManager.getSocialLoginContext(reverser='social-register')
        user = UserSerializer(request.user).data
        reg = [r.provider.provider for r in SocialAccountRegister.objects.filter(user=request.user)]
        for i in range(len(logins)):
            if (logins[i]['slug'] in reg):
                logins[i]['bg_color'] = "rgb(0 0 0 / 50%)"
                logins[i]['available'] = "false"
                logins[i]["link"] = reverse('social-revoke', kwargs={'provider':logins[i]['slug']})
            else:
                logins[i]['available'] = 'true'

        # # print(logins)
        return Str(request).render('dashboard.html', context={
            'user':user,
            'toasts':toasts.context,
            'authenticated':str(request.user.is_authenticated),
            'logins':logins
        })

    def post(self, request):
        data = request.POST
        try:
            if(data['password'] != data["_password"]): raise Exception('invalid_password')
            user:User = request.user
            if(data['password'] != None and data["password"] != "") : user.set_password(data["password"])
            if(data["phone"] != None and data["phone"] != ""): user.phone = data["phone"]
            ava:InMemoryUploadedFile = request.FILES.get('avatar')
            if(ava != None):
                user.avatar = ImageFile(ava.file, name=ava.name)
                # print(user.avatar)
            user.save()
        except Exception as e:
            return redirect(reverse('dashboard') + "?state=error_" + str(e))
        return redirect('dashboard')