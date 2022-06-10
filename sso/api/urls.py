from django.urls import include, path

from sso.api.views import AvailableSocialProvider, SocialOauthRegisterMe


urlpatterns = [
    path('account/', include('sso.api.account.urls')),
    path('res/', include('sso.api.res.urls')),
    path('net/', include('sso.api.net.urls')),
    path('auth/social/', AvailableSocialProvider.as_view(), name='available_social_provider'),
    path('auth/social/me/', SocialOauthRegisterMe.as_view(), name='social_oauth_register_me'),
]