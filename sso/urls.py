from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import include, path, reverse
from django.conf.urls.i18n import i18n_patterns
from django.contrib.admin.sites import AdminSite as AdminSiteTemplate
from django.views import View
from sso.lang.lang import Str
from sso.api.account.utils import generate_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name="dispatch")
class GeneratePassword(View):
    def post(self, request):
        passwd = request.POST["plain"]
        return  HttpResponse({'password':generate_password(passwd)})

urlpatterns = [
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)[0],
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)[0],
    path('setlang/<lang>/', Str.urlSetLang, name = "set_lang"),
    path("admin/logout/", lambda r: redirect("logout")),
    path("admin/login/", lambda r: redirect(reverse("login") + "?next=/admin/&state=alert_must_login")),
    path("register", lambda r: redirect('user-demo'), name='register'),
    path('api/', include('sso.api.urls')),
    path("", include('sso.auths.urls')),
    path("generate_password", GeneratePassword.as_view())
] + i18n_patterns(path('admin/', admin.site.urls),prefix_default_language=False)

admin.site.site_header = 'Dasbor Admin'
admin.site.index_title = 'Smandak Integrated System'