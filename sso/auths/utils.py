from django.conf import settings
from django.urls import reverse
from django_auth_ldap.backend import LDAPBackend
from oauth2_provider.models import Application

from sso.api.account.ldap import LDAP
from sso.auths.models import SocialOauthProvider

# from sso.api.account.utils import LDAPManager

class UserLoginData:
    def set_error(self, field, msg):
        try:
            self.error[field]
        except:
            self.error[field] = []
        
        self.error[field].append(msg)

    def __init__(self, request, post=False):
        if(post):
            request.data = request.POST

        self.request = request
        self.error = {}
        try:
            self.uid = request.data["uid"]
            if(self.uid == "" or self.uid == None): raise Exception
        except:
            self.set_error('uid', 'empty')
        
        try:
            self.password = request.data["password"]
            if(self.password == "" or self.password == None): raise Exception
        except:
            self.set_error('password', 'empty')

    def validate(self):
        return len(self.error) == 0

    def get_email(self):


        if(str(self.uid).isdigit()):
            email = LDAP().search_eid(self.uid)
            if(email == None):
                self.set_error('uid', 'Not Found')
            else:
                return email

        elif(settings.MAIN_DOMAIN in str(self.uid)):
            return self.uid
        else:
            return self.uid + "@" + settings.MAIN_DOMAIN
            

    def authenticate(self):
        email = self.get_email()
        if(self.validate()):
            user = LDAPBackend().authenticate(username=email, password=self.password, request=self.request)
            if(user == None):
                self.set_error('uid', 'Cannot Login')
            else:
                return user

class Toast:
    ERROR = "ERROR"
    ALERT = "ALERT"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    id = 0
    def __init__(self) -> None:
        self.context = []
    def create(self, body, type="INFO", header=None, show=True, timeout=None, id=None) -> None:
        out = {}
        if(id==None):
            id = f"toast-{type.lower()}-{Toast.id}"
            Toast.id += 1

        if(type == "INFO"):
            out = {
                "header": header or "str:info",
                "color":"rgba(0,0,255,0.25)",
            }
        elif(type == "ERROR"):
            out = {
                "header": header or "str:error",
                "color":"rgba(255,0,0,0.25)",
            }
        elif(type == "SUCCESS"):
            out = {
                "header": header or "str:success",
                "color":"rgba(0,255,0,0.25)",
            }
        elif(type == "ALERT"):
            out = {
                "header": header or "str:alert",
                "color":"rgba(255,255,0,0.25)",
            }
        else:
            return {}
        out["body"] = body
        out["show"] = str(show)
        out["id"] = id

        if(timeout != None):
            out["timeout"] = str(timeout)
        
        self.context.append(out)
        return out

def populate_sop_from_env(*args, **kwargs):
    index = 1
    for provider, v in {
        "facebook" : [
            settings.SOCIAL_AUTH_FACEBOOK_KEY,
            settings.SOCIAL_AUTH_FACEBOOK_SECRET
        ],
        "twitter" : [
            settings.SOCIAL_AUTH_TWITTER_KEY,
            settings.SOCIAL_AUTH_TWITTER_SECRET
        ],
        "google" : [
            settings.SOCIAL_AUTH_GOOGLE_KEY,
            settings.SOCIAL_AUTH_GOOGLE_SECRET
        ],
    }.items():
        if not ( v[0]  == "" or  v[1] == ""):
            SocialOauthProvider(
                provider=provider,
                key=v[0],
                secret=v[1],
                description="(Auto-generated)",
                order=index
            ).save()
            index += 1

def reverse_sop_from_env(*args, **kwargs):
    SocialOauthProvider.objects.filter(description__icontains='(Auto-generated)').delete()

def populate_application_oauth(*args, **kwargs):
    kwargs = {
        'client_id': settings.EMAIL_DEFAULT_CLIENT_ID,
        'client_secret': settings.EMAIL_DEFAULT_CLIENT_SECRET,
        'client_type':"confidential",
        'authorization_grant_type':"authorization-code",
        'redirect_uris':f'https://mail.{settings.MAIN_DOMAIN}/index.php/login/oauth',
        'name':'Webmail (Auto-generated)',
        'skip_authorization': True
    }
    Application(**kwargs).save()
    print("\n\nPlease set your webmail Oauth configuration data imediately\n")
    for i in kwargs:
        print(i, kwargs[i], sep = " : ")
    print('oauth_auth_uri :', 'https://sso.' + settings.MAIN_DOMAIN + reverse('authorize'))
    print('oauth_token_uri :', "https://sso." + settings.MAIN_DOMAIN + reverse('token'))

    kwargs = {
        'client_id': settings.APP_DEFAULT_CLIENT_ID,
        'client_secret':settings.APP_DEFAULT_CLIENT_SECRET,
        'client_type':"confidential",
        'authorization_grant_type':"authorization-code",
        'redirect_uris':f'https://app.{settings.MAIN_DOMAIN}/handler',
        'name':'Webapp (Auto-generated)',
        'skip_authorization': True
    }
    Application(**kwargs).save()
    print("\nPlease set your webapp Oauth configuration data imediately\n")
    for i in kwargs:
        print(i, kwargs[i], sep = " : ")
    print('oauth_auth_uri :', 'https://app.' + settings.MAIN_DOMAIN + reverse('authorize'))
    print('oauth_token_uri :', "https://app." + settings.MAIN_DOMAIN + reverse('token'))
    print()
def reverse_application_oauth(*args, **kwargs):
    Application.objects.filter(name__icontains='(Auto-generated)').delete()