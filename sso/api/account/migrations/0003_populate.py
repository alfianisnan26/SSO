# Generated by Django 4.0.4 on 2022-06-08 02:48

from datetime import timedelta
from django.conf import settings
from django.db import migrations
from sso.api.account.models import Profile, User
class Migration(migrations.Migration):
    def populate_profile(*args, **kwargs):
        profiles = [
            {
                'id':'GUEST',
                'name':'Tamu',
                'download_speed':2500000,
                'upload_speed':2500000,
                'download_quota':500000000,
                'upload_quota':500000000,
                'session_timeout': timedelta(hours=6),
                'shared_user':1,
            },
            {
                'id':'STUDENT',
                'name':'Siswa',
                'download_speed':5000000,
                'upload_speed':5000000,
                'download_quota':2000000000,
                'upload_quota':2000000000,
                'session_timeout':timedelta(hours=12),
                'shared_user':2,
            },
            {
                'id':'TEACHER',
                'name':'Guru',
                'download_speed':15000000,
                'upload_speed':15000000,
                'download_quota':5000000000,
                'upload_quota':5000000000,
                'session_timeout':timedelta(days=1),
                'shared_user':5,
            },
            {
                'id':'STAFF',
                'name':'Staff',
                'download_speed':15000000,
                'upload_speed':15000000,
                'download_quota':5000000000,
                'upload_quota':5000000000,
                'session_timeout':timedelta(days=1),
                'shared_user':5,
            },
            {
                'id':'ALUMNI',
                'name':'Alumni',
                'download_speed':5000000,
                'upload_speed':5000000,
                'download_quota':2000000000,
                'upload_quota':2000000000,
                'session_timeout':timedelta(hours=12),
                'shared_user':2,
            },
        ]
        
        for profile in profiles:
            profile["description"] = "(Auto-generated)"
            Profile(**profile).save()

    def revert_profile(*args, **kwargs):
        Profile.objects.filter(description__icontains="(Auto-generated)",).delete()

    
    def populate_superuser(*args, **kwargs):
        
        user = User(
            full_name = 'Admin Superuser',
            username = 'admin',
            email = 'admin@' + settings.MAIN_DOMAIN,
            profile = Profile.objects.get(id="STAFF"),
            permission_type = 'yes',
        )

        user.save()
        print('\n\nYour administrator (superuser) account is:')
        print('EMAIL    : ' + user.email)
        print('PASSWORD : ' + str(user.uuid))
        print('\nPlease be careful to save the credentials and change the password immediately on admin console')
        print('Do not rename the username!')
        print('\n')
    
    def revert_superuser(*args, **kwargs):
        User.objects.filter(username = 'admin').delete()

    dependencies = [
        ('account', '0002_remove_registrant_profile_remove_registrant_uuid_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_profile, revert_profile),
        migrations.RunPython(populate_superuser, revert_superuser),
    ]