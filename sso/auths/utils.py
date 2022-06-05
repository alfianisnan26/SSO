from django.conf import settings
from django_auth_ldap.backend import LDAPBackend

from sso.api.account.ldap import LDAP

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
    def __init__(self) -> None:
        self.context = []
    def create(self, body, type="INFO", header=None, show=True, timeout=None) -> None:
        out = {}
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

        if(timeout != None):
            out["timeout"] = str(timeout)
        
        self.context.append(out)
        return out
        