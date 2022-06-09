from django.urls import include, path, re_path

from sso.api.account.views import UserMeView

urlpatterns = [
    path('users/me/', UserMeView.as_view(), name='user-me'),
]