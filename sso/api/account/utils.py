import os
import datetime
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
import ldap 
import ldap.modlist as modlist
from ldap.ldapobject import LDAPObject
import os
import sys
import time
from subprocess import Popen, PIPE
from typing import List, Dict
import re
import ldif

def upload_avatar(instance, filename):
    full_path = os.path.join(settings.MEDIA_ROOT, 'users', instance.uuid)
    if(os.path.exists(full_path)):
        for file in os.listdir(full_path):
            if("avatar" in file):
                os.remove(full_path + "/" + file)
    file_ext = filename.split('.')[-1]
    file = os.path.join('users', instance.uuid, filename)
    return file

# LDAP server address.
LDAP_URI = settings.AUTH_LDAP_SERVER_URI

# LDAP base dn.
BASEDN = settings.LDAP_BASEDN

# Bind dn/password
BINDDN = settings.AUTH_LDAP_BIND_DN
BINDPW = settings.AUTH_LDAP_PASSWORD
MAIN_DOMAIN = settings.MAIN_DOMAIN

# Storage base directory.
STORAGE_BASE_DIRECTORY = '/var/vmail/vmail1'

# Append timestamp in maildir path.
APPEND_TIMESTAMP_IN_MAILDIR = True

# Get base directory and storage node.
std = STORAGE_BASE_DIRECTORY.rstrip('/').split('/')
STORAGE_NODE = std.pop()
STORAGE_BASE = '/'.join(std)

# Hashed maildir: True, False.
# Example:
#   domain: domain.ltd,
#   user:   zhang (zhang@domain.ltd)
#
#       - hashed: d/do/domain.ltd/z/zh/zha/zhang/
#       - normal: domain.ltd/zhang/
HASHED_MAILDIR = True

# Default password schemes.
# Multiple passwords are supported if you separate schemes with '+'.
# For example: 'SSHA+NTLM', 'CRAM-MD5+SSHA', 'CRAM-MD5+SSHA+MD5'.
DEFAULT_PASSWORD_SCHEME = 'SSHA512'

# Do not prefix password scheme name in password hash.
HASHES_WITHOUT_PREFIXED_PASSWORD_SCHEME = ['NTLM']
# ------------------------------------------------------------------

def __str2bytes(s) -> bytes:
    """Convert `s` from string to bytes."""
    if isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode()
    elif isinstance(s, (int, float)):
        return str(s).encode()
    else:
        return bytes(s)

# Return list of modification operation.
def mail_to_user_dn(mail):
    """Convert email address to ldap dn of normail mail user."""
    if mail.count('@') != 1:
        return ''

    user, domain = mail.split('@')

    # User DN format.
    # mail=user@domain.ltd,domainName=domain.ltd,[LDAP_BASEDN]
    dn = 'mail=%s,ou=Users,domainName=%s,%s' % (mail, domain, BASEDN)

    return dn


def generate_password(plain_password, scheme=DEFAULT_PASSWORD_SCHEME):
    """Generate password hash with `doveadm pw` command.
    Return SSHA instead if no 'doveadm' command found or other error raised."""

    scheme = scheme.upper()
    p = str(plain_password).strip()

    pp = Popen(['doveadm', 'pw', '-s', scheme, '-p', p], stdout=PIPE)
    pw = pp.communicate()[0]

    if scheme in HASHES_WITHOUT_PREFIXED_PASSWORD_SCHEME:
        pw.lstrip('{' + scheme + '}')

    # remove '\n'
    pw = pw.strip()

    return pw.decode("utf-8")

def get_days_of_today():
    """Return number of days since 1970-01-01."""
    today = datetime.date.today()

    try:
        return (datetime.date(today.year, today.month, today.day) - datetime.date(1970, 1, 1)).days
    except:
        return 0

def ldif_mailuser(user, quota):
    # Append timestamp in maildir path
    DATE = time.strftime('%Y.%m.%d.%H.%M.%S')
    TIMESTAMP_IN_MAILDIR = ''
    if APPEND_TIMESTAMP_IN_MAILDIR:
        TIMESTAMP_IN_MAILDIR = '-%s' % DATE

    username = user.username

    mail = username + '@' + MAIN_DOMAIN
    dn = mail_to_user_dn(mail)

    maildir_domain = MAIN_DOMAIN.lower()
    if HASHED_MAILDIR is True:
        str1 = str2 = str3 = username[0]
        if len(username) >= 3:
            str2 = username[1]
            str3 = username[2]
        elif len(username) == 2:
            str2 = str3 = username[1]

        maildir_user = "%s/%s/%s/%s%s/" % (str1, str2, str3, username, TIMESTAMP_IN_MAILDIR, )
        mailMessageStore = maildir_domain + '/' + maildir_user
    else:
        mailMessageStore = "%s/%s%s/" % (MAIN_DOMAIN, username, TIMESTAMP_IN_MAILDIR)

    homeDirectory = STORAGE_BASE_DIRECTORY + '/' + mailMessageStore
    mailMessageStore = STORAGE_NODE + '/' + mailMessageStore

    _ldif = {
        'accountStatus' : "active",
        'objectClass': ['inetOrgPerson', 'mailUser', 'shadowAccount', 'amavisAccount'],
        'mail': mail,
        'userPassword': user.password,
        'mailQuota': quota,
        'cn': user.full_name,
        'sn': username,
        'uid': username,
        'employeeNumber':user.eid,
        'employeeType':user.user_type,
        'mailboxFolder': "Maildir",
        'mailboxFormat': "maildir",
        'shadowLastChange' : get_days_of_today(),
        'domainGlobalAdmin': "yes" if user.is_superuser else "no",  
        'storageBaseDirectory': STORAGE_BASE,
        'mailMessageStore': mailMessageStore,
        'homeDirectory': homeDirectory,
        'accountStatus': 'active',
        'enabledService': ['internal', 'doveadm', 'lib-storage',
                           'indexer-worker', 'dsync', 'quota-status',
                           'mail',
                           'smtp', 'smtpsecured', 'smtptls',
                           'pop3', 'pop3secured', 'pop3tls',
                           'imap', 'imapsecured', 'imaptls',
                           'managesieve', 'managesievesecured', 'managesievetls',
                           'sieve', 'sievesecured', 'sievetls',
                           'deliver', 'lda', 'lmtp', 'forward',
                           'senderbcc', 'recipientbcc',
                           'sogo', 'sogowebmail', 'sogocalendar', 'sogoactivesync',
                           'displayedInGlobalAddressBook'],
        'shadowLastChange': str(get_days_of_today()),
        'amavisLocal': 'TRUE',
    }

    return dn, _ldif

# class LDAPManager:
#     def start() -> LDAPObject:
#         l = ldap.initialize(LDAP_URI) 
#         l.bind(BINDDN, BINDPW) 
#         return l

#     def deleteUser(mail):
#         try:
#             l = LDAPManager.start()
#             dn = "mail=" + mail +",ou=Users,domainName="+ MAIN_DOMAIN+","+ BASEDN
#             l.delete_s(dn)
#             l.unbind_s()
#             LDAPManager.updateAdminUser(mail, False, without_update_user = True)
#             return True
#         except:
#             return False
        
#     def updateEntry(mail, key, value):
#         print("DATA UPDATE ENTRY", value)
#         l = ldap.initialize(LDAP_URI) 
#         l.bind(BINDDN, BINDPW) 
#         dn = "mail=" + mail +",ou=Users,domainName="+ MAIN_DOMAIN+","+ BASEDN
#         ldif = l.search_s(dn, ldap.SCOPE_SUBTREE,"(mail=*)", None)[0][1][key]
#         print(ldif)
#         ldifs = modlist.modifyModlist({key: ldif}, {key: value})
#         l.modify_s(dn, ldifs)
#         l.unbind_s()

#     def saveUser(user):
#         print("SAVING USER TO LDAP SERVER")

#     def updateFullName(mail, fullname):
#         LDAPManager.updateEntry(mail, "cn", fullname)
#         return fullname

#     def updatePassword(mail, password):
#         password = generate_password_with_doveadmpw(password)
#         LDAPManager.updateEntry(mail, "userPassword", [password.encode("utf-8")])
#         return password

#     def updateAdminUser(mail, is_superuser, without_update_user = False):
#         l = ldap.initialize(LDAP_URI) 
#         l.bind(BINDDN, BINDPW) 
#         dn = "cn=admin,ou=Groups,domainName="+ MAIN_DOMAIN+","+ BASEDN
#         ldif = l.search_s(dn, ldap.SCOPE_SUBTREE,"(cn=*)", None)[0][1]
#         try:
#             ldif = ldif["memberUid"]
#             ldif_old = {"memberUid" : ldif}
#         except:
#             ldif_old = {}
#             ldif = []
#         try:
#             ldif.remove(mail.replace("@" + MAIN_DOMAIN, "").encode("utf-8"))
#         except:
#             pass
#         if is_superuser:
#             ldif.append(mail.replace("@" + MAIN_DOMAIN, "").encode("utf-8"))
#             if(not without_update_user): LDAPManager.updateEntry(mail, "domainGlobalAdmin", ["yes".encode("utf-8")])
#         else:
#             if(not without_update_user):LDAPManager.updateEntry(mail, "domainGlobalAdmin", ["no".encode("utf-8")])
#         ldifs = modlist.modifyModlist(ldif_old, {"memberUid" : ldif})
#         l.modify_s(dn, ldifs)
#         l.unbind_s()
        
#     def create(user):
#         dn, data = ldif_mailuser(user, "524288")
#         l = ldap.initialize(LDAP_URI) 
#         l.bind(BINDDN, BINDPW) 
#         data_mod = {}
#         for k,v in data.items():
#             if(isinstance(v, list)):
#                 data_mod[k] = [val.encode('utf-8') for val in v]
#             else: data_mod[k] = v.encode('utf-8')
#         ldifs = modlist.addModlist(data_mod)
#         l.add_s(dn, ldifs)
#         l.unbind_s()
#         if(user.is_superuser == True):
#             user.is_staff = user.is_superuser
#             LDAPManager.updateAdminUser(user)
#         return data

#     def search_eid(eid):
#         conn = ldap.initialize(LDAP_URI)
#         conn.set_option(ldap.OPT_REFERRALS, 0)
#         conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_PASSWORD)

#         basedn = "ou=Users,domainName=" + settings.MAIN_DOMAIN + "," + settings.LDAP_BASEDN
#         searchScope = ldap.SCOPE_SUBTREE
#         searchFilter = "employeeNumber=%s" % eid
        
#         res = conn.search_s(basedn, searchScope, searchFilter, ['mail'])
#         try:
#             return res[0][1]['mail'][0].decode('UTF-8')
#         except:
#             return None

    