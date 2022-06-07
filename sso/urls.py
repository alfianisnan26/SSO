from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.conf.urls.i18n import i18n_patterns

from sso.lang.lang import Str

urlpatterns = [
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)[0],
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)[0],
    path('setlang/<lang>/', Str.urlSetLang, name = "set_lang"),
    path("admin/logout/", lambda r: redirect("logout")),
    path("admin/login/", lambda r: redirect(reverse("login") + "?next=/admin/&state=alert_must_login")),
    path('api/', include('sso.api.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("", include('sso.auths.urls')),
] + i18n_patterns(path('admin/', admin.site.urls),prefix_default_language=False)

admin.site.site_header = 'Dasbor Admin'
admin.site.index_title = 'Smandak Integrated System'