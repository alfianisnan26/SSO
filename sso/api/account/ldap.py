from django.conf import settings
import ldap
import ldap.modlist as modlist

import hashlib
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from sso.api.account.utils import MAIN_DOMAIN, ldif_mailuser

class LDAP:
    URI = settings.AUTH_LDAP_SERVER_URI
    DN = settings.AUTH_LDAP_BIND_DN
    PASS = settings.AUTH_LDAP_PASSWORD
    MAIN_DOMAIN = settings.MAIN_DOMAIN
    BASE_DN = "ou=Users,domainName=" + MAIN_DOMAIN + ","+ settings.LDAP_BASEDN
    SCOPE_SUBTREE = ldap.SCOPE_SUBTREE

    def __init__(self) -> None:
        self.h = ldap.initialize(LDAP.URI)
        self.h.set_option(ldap.OPT_REFERRALS, 0)

    def bind(self):
        print("BIND")
        self.h.simple_bind_s(LDAP.DN, LDAP.PASS)
        return self.h

    def unbind(self):
        print("UNBIND")
        self.h.unbind_s()
        return self.h

    def search_eid(self, eid):
        self.bind()
        searchScope = LDAP.SCOPE_SUBTREE
        searchFilter = "employeeNumber=%s" % eid
        
        res = self.h.search_s(LDAP.BASE_DN, searchScope, searchFilter, ['mail'])
        self.unbind()

        try:
            return res[0][1]['mail'][0].decode('UTF-8')
        except:
            return None

    def get_dn(user):
        return ",".join([f"mail={user}", LDAP.BASE_DN])

    def save_user(self, user):
        self.bind()
        dn = LDAP.get_dn(user)
        try:
            ldif = self.h.search_s(dn, LDAP.SCOPE_SUBTREE)
        except:
            dn, ldif =  ldif_mailuser(user, "524288")
        
        print(ldif, dn)
        self.unbind()