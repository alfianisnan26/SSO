from django.urls import include, path


urlpatterns = [
    path('account/', include('sso.api.account.urls')),
    path('res/', include('sso.api.res.urls')),
]