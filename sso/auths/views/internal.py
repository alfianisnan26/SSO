from datetime import datetime, timedelta
from email.mime import application
import json
import traceback
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from oauth2_provider.models import Grant, Application
import pytz
from requests import request
from sso import settings
from sso.api.account.models import User
from sso.api.account.serializers import UserMinimalSerializer, UserSerializer
from sso.api.account.utils import generate_password

from sso.auths.models import ProviderManager, SocialOauthProvider
from sso.auths.utils import UserLoginData, redirect_query
from sso.auths.utils import Toast
from sso.lang.lang import Str
from django.shortcuts import redirect, render
from django.contrib.auth import views
from django.views import View
from django.contrib.auth import logout as auth_logout
import urllib.parse

def parse_queries(queries):
    qp = ""
    lenq = len(queries) 
    if(lenq > 0):
        qp = "?"
        for i in queries.keys():
            qp += f"{i}={queries[i]}&"
    return qp[:-1]

class LogoutView(View):
    def get(self, request):
        auth_logout(request)
        return redirect(reverse('login') + "?state=success_logout")

class LoginView(views.LoginView):

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        uld = UserLoginData(request, post=True)
        request.POST._mutable = True
        email = uld.get_email()
        request.POST['username'] = email
        try:
            user = User.objects.get(email = email)
        except:
            return redirect(reverse('login-email') + "?" + request.META['QUERY_STRING'] + "&state=alert_user_not_found")

        if(not user.is_active):
            return redirect(reverse('login-email') + "?" + request.META['QUERY_STRING'] + "&state=alert_user_inactive")
        
        out = super().post(request, *args, **kwargs)
        if(not out.status_code == 302):
            return redirect(reverse('login-email') + "?" + request.META['QUERY_STRING'] + "&state=error_cannot_login")
        return out

    def dispatch(self, request, *args, **kwargs):
        self.social_available = SocialOauthProvider.objects.filter(is_active=True).exists()
        if(request.user.is_authenticated):
            User.update(request)
            return redirect_query('home', request)
        elif(not self.social_available and request.path == reverse('login')):
            return redirect_query('login-email', request)
            
        self.strs = Str(request)
        self.queries = request.GET

        resp = super().dispatch(request, *args, **kwargs)
        return self.strs.setLang(resp)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            next = urllib.parse.quote(self.queries["next"])
        except:
            next = "/"

        toasts = Toast()
        try:
            state = self.queries["state"]
            toasts.create(f"str:{state}", header = 'str:cannot_login' if state == 'error_cannot_login' or state == 'error_msyacw' else None, type=state.split("_")[0].upper(), timeout=5)
        except:
            pass
        context = self.strs.setContext({
                    "social_available" : str(self.social_available),
                    "toasts":toasts.context,
                    "url_smart_login" : "/login/",
                    "logins" : ProviderManager.getSocialLoginContext(next) + [{
                        "link" : reverse('login-email') + f"?next={next}",
                        "name" : "Email",
                        "slug" : "email",
                        "icon" : "/static/assets/icons/em.png",
                        "color": "grey",
                        "bg_color": "white",
                    }]
                })

        return context

class WelcomeView(View):
    def get(self, request):
        if(not request.user.is_authenticated):
            print(request.GET)
            return redirect_query('login', request)
        User.update(request)
        toasts = Toast()
        try:
            next = request.GET["next"]
            if(next == '/'): raise Exception("redirect to root")
            toasts.create(
                Str(request).get("redirect_message") + ", <br><a href=%s><button class='small'>%s</button></a>" %  (next, Str(request).get("click_here")),
                type=toasts.INFO,
                # timeout=3,
                header="str:redirect"
            )
        except Exception as e:
            next = ''

        try:
            state = request.GET["state"]
            toasts.create(f"str:{state}", type=state.split("_")[0].upper(), timeout=5)
        except Exception as e:
            pass

        app = Application.objects.get(
                client_id = settings.APP_DEFAULT_CLIENT_ID
            )
        user:User = request.user
        
        menus:list = [
            {
                "name":"str:webmail",
                "icon":"fa-solid fa-envelope",
                "color": "#F2C94C",
                "url":"str:webmail_url"
            },
            {
                "name":"str:main_sites",
                "icon":"fa-solid fa-earth-asia",
                "color":"#7B61FF",
                "url":"str:main_sites_url"
            },
            # {
            #     "name":"str:lms",
            #     "icon":"fa-solid fa-graduation-cap",
            #     "color":"#0093DD",
            #     "url":"str:lms_url"
            # },
            {
                "name":"str:speed_test",
                "icon":"fa-solid fa-gauge-high",
                "color":"#0093DD",
                "url":"str:speed_test_url"
            },
            {
                "preloading" : app.redirect_uris.split(' ')[0],
                "name":"str:dashboard",
                "icon":"fa-solid fa-screwdriver-wrench",
                "color":"#FF1818",
                # TODO OAuth Code for App.Smandak
                "url": reverse('grant', kwargs={'app':app.client_id})
            }
        ]
        return Str(request).render('home.html', context={
        "menus" : menus,   
        "toasts": toasts.context,
        "redirect" : next, # urllib.parse.unquote(next),
        "authenticated" : str(request.user.is_authenticated),
        "profile":{
            'name':user.full_name,
            "role":user.user_type,
            "permission":user.permission_type,
            "rolename":f"str:{user.user_type}",
            "url_pic": user.get_avatar(placeholder=True)
        }})

class RegistrationFormView(View):
    def get(self, request):
        return Str(request).render('guest.html')

    def post(self, request):
        data = request.POST
        try:
            if(data['eid'] == '' or data['eid'] == None): raise Exception('eid')
            if(not data['password'] == data['_password'] or data['password'] == ''): raise Exception('passwd')
            password = generate_password(data['password'])
            user = User(
                full_name = data['name'],
                eid = data['eid'],
                phone = data['phone'],
                user_type='GUEST',
                password = password,
                is_active=False
            )
            user.save()
            return Str(request).render('userme.html', context = {'user': UserSerializer(user).data})
        except Exception as e:
            traceback.print_exc()
            toasts = Toast()
            if('duplicate key' in str(e)):
                toasts.create("NIS/NIP sudah teregistrasi sebelumnya,<br>Silahkan hubungi admin.", type=toasts.ERROR)
            elif('eid' in str(e)):
                toasts.create("NIS/NIP tidak boleh kosong", toasts.ERROR)
            elif('passwd' in str(e)):
                toasts.create("Kata sandi anda mungkin kosong atau tidak cocok", toasts.ERROR)
            elif('16' in str(e)):
                toasts.create("Nomor telepon yang anda masukkan tidak valid", toasts.ERROR)
            else:
                toasts.create(str(e), type=toasts.ERROR)
            return Str(request).render('guest.html', context={'toasts': toasts.context})