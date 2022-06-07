from datetime import datetime, timedelta
from email.mime import application
import json
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from oauth2_provider.models import Grant, Application
import pytz
from requests import request
from sso import settings
from sso.api.account.models import User

from sso.auths.models import ProviderManager, SocialOauthProvider
from sso.auths.utils import UserLoginData
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
        request.POST['username'] = uld.get_email()
        out = super().post(request, *args, **kwargs)
        if(not out.status_code == 302):
            return redirect(reverse('login-email') + "?" + request.META['QUERY_STRING'] + "&state=error_cannot_login")
        return out

    def dispatch(self, request, *args, **kwargs):
        self.social_available = SocialOauthProvider.objects.filter(is_active=True).exists()
        if(request.user.is_authenticated):
            return redirect('home')
        elif(not self.social_available and request.path == reverse('login')):
            return redirect('login-email')
            
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
            return redirect('login')
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
            {
                "name":"str:lms",
                "icon":"fa-solid fa-graduation-cap",
                "color":"#0093DD",
                "url":"str:lms_url"
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