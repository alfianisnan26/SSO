import base64
import os
from django.conf import settings
import ldap
import ldap.modlist as modlist

import hashlib
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from sso.api.account.utils import MAIN_DOMAIN, ldif_mailuser, mail_to_user_dn

class LDAP:
    URI = settings.AUTH_LDAP_SERVER_URI
    DN = settings.AUTH_LDAP_BIND_DN
    PASS = settings.AUTH_LDAP_PASSWORD
    MAIN_DOMAIN = settings.MAIN_DOMAIN
    BASE_DN = "ou=Users,domainName=" + MAIN_DOMAIN + ","+ settings.LDAP_BASEDN
    SCOPE_SUBTREE = ldap.SCOPE_SUBTREE

    IGNORED_ATTR = ['enabledService', 'homeDirectory', 'mailboxFolder', 'mailboxFormat', 'mailMessageStore', 'objectClass', 'storageBaseDirectory', 'amavisLocal']

    def __init__(self) -> None:
        self.h = ldap.initialize(LDAP.URI)
        self.h.set_option(ldap.OPT_REFERRALS, 0)

    def bind(self, dn=None, passwd=None):
        self.h.simple_bind_s(dn or LDAP.DN, passwd or LDAP.PASS)
        return self.h

    def unbind(self):
        # print("UNBIND")
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

    def delete_user(self, user):
        self.bind()
        error = True
        try:
            dn = mail_to_user_dn(user.email)
            self.h.delete_s(dn)
            error = False
        except Exception as e:
            print(e)
        self.unbind()
        return error

    def update_user(self, user):
        if(user.user_type == "GUEST"): return False
        self.bind()
        dn, ldif =  ldif_mailuser(user)
        try:
            dn, ldif_old = self.h.search_s(dn, LDAP.SCOPE_SUBTREE, "(mail=*)", None)[0]
            self.h.modify_s(dn, modlist.modifyModlist(ldif_old, ldif, ignore_attr_types=LDAP.IGNORED_ATTR))
        except Exception as e:
            self.h.add_s(dn,  modlist.addModlist(ldif))
        self.unbind()

    def authenticate(self, user, raw_password):
        try:
            self.bind(dn=mail_to_user_dn(user.email), passwd=raw_password)
            return True
        except ldap.INVALID_CREDENTIALS:
            return False
        
        