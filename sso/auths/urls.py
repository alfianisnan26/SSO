from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import include, path
from oauth2_provider.views import AuthorizationView
from rest_framework.response import Response
from sso.api.account.views import Dashboard
from sso.auths.views.internal import LoginView, LogoutView, RegistrationFormView, WelcomeView
from sso.auths.views.oauth import GrantView, TokenViewOauth
from sso.auths.views.socials import OauthCallback, OauthLogin, OauthRegister, OauthRevoke
from sso.lang.lang import Str


def forgot_password(request:HttpRequest):
    return Str(request).render('forgot_password.html')

def guest_info(request:HttpRequest):
    return Str(request).render('guest.html')

urlpatterns = [
    path('account/forgot_password/', forgot_password, name="forgot-password"),
    path('account/guest/', RegistrationFormView.as_view(), name="guest"),
    path("login/email/", LoginView.as_view(template_name='login-email.html', next_page="home") , name="login-email"),
    path("login/", LoginView.as_view(template_name='login-smart.html') , name="login"),
    path("logout/", LogoutView.as_view() , name="logout"),
    path('menu/about/', lambda r : Str(r).render("about.html", context={"authenticated":str(r.user.is_authenticated)}), name="about"),
    path('menu/help/', lambda r : Str(r).render("help.html", context={"authenticated":str(r.user.is_authenticated)}), name="help"),
    path('auth/oauth/token/', TokenViewOauth.as_view(), name="token"),
    path('auth/oauth/authorize/', AuthorizationView.as_view(), name="authorize" ),
    path('auth/oauth/grant/<app>', GrantView.as_view(), name="grant" ),
    path('auth/social/handler/', OauthCallback.as_view(), name = "social-handler"),
    path('auth/social/<str:provider>/', OauthLogin.as_view(), name = "social-login"),
    path('auth/social/<str:provider>/register/', OauthRegister.as_view(), name = "social-register"),
    path('auth/social/<str:provider>/revoke/', OauthRevoke.as_view(), name = "social-revoke"),
    path('dashboard/', Dashboard.as_view(), name = "dashboard"),
    path("", WelcomeView.as_view(), name="home"),
]