import base64
import io
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
from django.contrib.auth.hashers import BasePasswordHasher

import random
import string

import requests

def randStr(chars = string.ascii_lowercase + string.ascii_uppercase + string.digits, N=64):
	return ''.join(random.choice(chars) for _ in range(N))

def upload_avatar(instance, filename):
    full_path = os.path.join(settings.MEDIA_ROOT, 'users', str(instance.uuid), 'avatar')
    if(os.path.exists(full_path)):
        for file in os.listdir(full_path):
            if("avatar" in file):
                os.remove(full_path + "/" + file)
    file = os.path.join('users', str(instance.uuid), 'avatar', f'avatar-{randStr()}.png')
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

HASHED_MAILDIR = True

DEFAULT_PASSWORD_SCHEME = 'SSHA512'

HASHES_WITHOUT_PREFIXED_PASSWORD_SCHEME = ['NTLM']
# ------------------------------------------------------------------

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
    try:
        """Generate password hash with `doveadm pw` command.
        Return SSHA instead if no 'doveadm' command found or other error raised."""

        scheme = scheme.upper()
        p = str(plain_password).strip()

        pp = Popen(['doveadm', 'pw', '-s', scheme, '-p', p], stdout=PIPE)
        pw = pp.communicate()[0]

        if scheme in HASHES_WITHOUT_PREFIXED_PASSWORD_SCHEME:
            pw.lstrip('{' + scheme + '}')
        # print(pw)
        # remove '\n'
        pw = pw.strip()
    except:
        resp = requests.post('https://sso.smandak.sch.id/generate_password', {'plain':plain_password})
        pw = resp.content

    return pw.decode("utf-8")

def data_encoder(_ldif):
    data_mod ={}

    for k,v in _ldif.items():
        try:
            if(isinstance(v, list)):
                data_mod[k] = [val.encode('utf-8') for val in v]
            else: data_mod[k] = [v.encode('utf-8')]
        except Exception as e:
            # print(k, e)
            pass
    return data_mod

def get_days_of_today():
    """Return number of days since 1970-01-01."""
    today = datetime.date.today()

    try:
        return (datetime.date(today.year, today.month, today.day) - datetime.date(1970, 1, 1)).days
    except:
        return 0

def ldif_mailuser(user, quota=settings.DEFAULT_EMAIL_QUOTA):
    # Append timestamp in maildir path
    DATE = time.strftime('%Y.%m.%d.%H.%M.%S')
    TIMESTAMP_IN_MAILDIR = ''
    if APPEND_TIMESTAMP_IN_MAILDIR:
        TIMESTAMP_IN_MAILDIR = '-%s' % DATE

    dn = mail_to_user_dn(user.email)

    maildir_domain = MAIN_DOMAIN.lower()
    if HASHED_MAILDIR is True:
        str1 = str2 = str3 = user.username[0]
        if len(user.username) >= 3:
            str2 = user.username[1]
            str3 = user.username[2]
        elif len(user.username) == 2:
            str2 = str3 = user.username[1]

        maildir_user = "%s/%s/%s/%s%s/" % (str1, str2, str3, user.username, TIMESTAMP_IN_MAILDIR, )
        mailMessageStore = maildir_domain + '/' + maildir_user
    else:
        mailMessageStore = "%s/%s%s/" % (MAIN_DOMAIN, user.username, TIMESTAMP_IN_MAILDIR)

    homeDirectory = STORAGE_BASE_DIRECTORY + '/' + mailMessageStore
    # mailMessageStore = STORAGE_NODE + '/' + mailMessageStore
    

    _ldif = {
        # 'jpegPhoto' : user,
        'accountStatus' : "active" if user.is_active else "inactive",
        'mobile' : user.phone,
        'objectClass': ['inetOrgPerson', 'mailUser', 'shadowAccount', 'amavisAccount'],
        'mail': user.email,
        'userPassword': user.password,
        'mailQuota': quota,
        'cn': user.full_name,
        'sn': user.username,
        'uid': user.username,
        'employeeNumber':user.eid,
        'employeeType':user.user_type,
        'mailboxFolder': "Maildir",
        'mailboxFormat': "maildir",
        'shadowLastChange' : get_days_of_today(),
        'domainGlobalAdmin': user.permission_type,  
        # 'storageBaseDirectory': STORAGE_BASE,
        # 'mailMessageStore': mailMessageStore,
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
    

    data_mod = data_encoder(_ldif)

    if(not (user.avatar.name == '' or user.avatar.name == None)):
        try:
            file = open(os.path.join(settings.MEDIA_ROOT, user.avatar.name), 'rb')
            data_mod['jpegPhoto'] = [file.read()]
        except Exception as e:
            print("HERE" , e)
    
    return dn, data_mod