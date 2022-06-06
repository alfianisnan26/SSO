from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import include, path
from sso.auths.views.internal import LoginView, LogoutView, WelcomeView
from sso.auths.views.oauth import TokenView, AuthorizationView
from sso.auths.views.socials import OauthCallback, OauthLogin
from sso.lang.lang import Str


def forgot_password(request:HttpRequest):
    return Str(request).render('forgot_password.html')

def guest_info(request:HttpRequest):
    return Str(request).render('guest.html')

urlpatterns = [
    path('account/forgot_password/', forgot_password, name="forgot-password"),
    path('account/guest/', guest_info, name="guest"),
    path("login/email/", LoginView.as_view(template_name='login-email.html', next_page="home") , name="login-email"),
    path("login/", LoginView.as_view(template_name='login-smart.html') , name="login"),
    path("logout/", LogoutView.as_view() , name="logout"),
    path('menu/about/', lambda r : Str(r).render("about.html"), name="about"),
    path('menu/help/', lambda r : Str(r).render("help.html"), name="help"),
    path('auth/oauth/token/', TokenView.as_view(), name="token"),
    path('auth/oauth/authorize/', AuthorizationView.as_view(), name="authorize" ),
    path('auth/social/handler/', OauthCallback.as_view(), name = "social-handler"),
    path('auth/social/<str:provider>/', OauthLogin.as_view(), name = "social-login"),
    path("", WelcomeView.as_view(), name="home"),
]