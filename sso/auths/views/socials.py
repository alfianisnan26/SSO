from django.http import HttpRequest
from django.shortcuts import redirect, render
from sso.api.account.models import SocialMediaAccount
from sso.auths.serializers import SocialMediaAccountSerializer
from sso.lang.lang import Str
from urllib.parse import urlencode, quote
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse_lazy
from rest_framework import views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.reverse import reverse
from requests_oauthlib import OAuth2Session
from requests_oauthlib import OAuth1
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import requests
from rest_framework_simplejwt.tokens import RefreshToken, Token
from twython import Twython
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_auth_ldap.backend import LDAPBackend           
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.http import HttpResponse 
from django.views.static import serve
from django.template.loader import render_to_string
import os

class StaticOauthFlow:
    google_token_url = "https://www.googleapis.com/oauth2/v4/token"
    google_userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    google_authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    facebook_authorization_base_url = 'https://www.facebook.com/dialog/oauth'
    facebook_token_url = 'https://graph.facebook.com/oauth/access_token'
    facebook_userinfo_url = 'https://graph.facebook.com/v12.0/me?fields=id,name,picture{url},email'
    
    twitter_token_url = u"https://api.twitter.com/oauth/request_token"
    twitter_authorization_base_url = u"https://api.twitter.com/oauth/authorize"
    twitter_access_url = u"https://api.twitter.com/oauth/access_token"
    
    def google(request, do, access):
        return OAuth2Session(settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, 
                             state=access,
                             scope=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE, redirect_uri=reverse("oauth2-handler", request=request, kwargs={'do':do,'provider':"google"}).replace("http://","https://"))
    def facebook(request, do, access):
        facebook = OAuth2Session(settings.SOCIAL_AUTH_FACEBOOK_KEY,
                                state=access,
                                 scope=settings.SOCIAL_AUTH_FACEBOOK_SCOPE, redirect_uri=reverse("oauth2-handler", request=request, kwargs={'do':do,'provider':"facebook"}).replace("http://","https://"))
        facebook = facebook_compliance_fix(facebook)
        return facebook
    
class OauthCallback(views.APIView):
    def get(self, request, provider, do): 
        try:
            token = request.query_params["state"]
            data = {"detail":"Provider does not support"}
            statusOut = status.HTTP_400_BAD_REQUEST
            if(provider == "google"):
                google = StaticOauthFlow.google(request, do, token)
                google.fetch_token(StaticOauthFlow.google_token_url, client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                        code=request.query_params["code"])
                r = google.get(StaticOauthFlow.google_userinfo_url)
                data = r.json()
                data = {
                    "uid" : data["id"],
                    "uname" : data["email"],
                    "upic" : data["picture"],
                    "name" : data["name"],
                }
                statusOut = status.HTTP_200_OK
            elif(provider == "facebook"):
                facebook = StaticOauthFlow.facebook(request, do, token)
                facebook.fetch_token(StaticOauthFlow.facebook_token_url, client_secret=settings.SOCIAL_AUTH_FACEBOOK_SECRET,
                        code= request.query_params["code"])
                data = (facebook.get(StaticOauthFlow.facebook_userinfo_url)).json()
                data = {
                    "uid" : data["id"],
                    "uname":data["email"],
                    "upic":data["picture"]["data"]["url"],
                    "name":data["name"],
                }
                statusOut = status.HTTP_200_OK
            elif(provider == "twitter"):
                oauth_token = request.query_params.get("oauth_token")
                oauth_verifier = request.query_params.get("oauth_verifier")
                oauth = OAuth1(
                    settings.SOCIAL_AUTH_TWITTER_KEY, 
                    client_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                    resource_owner_key=oauth_token,
                    verifier=oauth_verifier,)
                res = requests.post(f"https://api.twitter.com/oauth/access_token", auth=oauth)
                res_split = res.text.split("&")
                oauth_token = res_split[0].split("=")[1]
                oauth_secret = res_split[1].split("=")[1]
                user_id = res_split[2].split("=")[1] if len(res_split) > 2 else None
                user_name = res_split[3].split("=")[1] if len(res_split) > 3 else None

                statusOut = status.HTTP_200_OK
                t = Twython(app_key=settings.SOCIAL_AUTH_TWITTER_KEY,
                    app_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
                    oauth_token=oauth_token,
                    oauth_token_secret=oauth_secret)
                api = 'https://api.twitter.com/1.1/users/show.json'
                args = {'screen_name': user_name}
                resp = t.request(api, params=args)
                data = {
                    "uid":user_id,
                    "uname":user_name,
                    "upic":resp['profile_image_url_https'],
                    "name": resp['screen_name'],
                }
                
            if(do == "login"):
                account = get_object_or_404(SocialMediaAccount, uid = provider + "_" + data["uid"])
                refresh = RefreshToken.for_user(account.user)
                
                account.uname = data["uname"]
                account.upic = data["upic"]
                account.name = data["name"]
                account.save()  
                response = redirect(token + "?access={access}".format(access=str(refresh.access_token)))
                return response.set_cookie("refresh", str(refresh.access))
                
            elif(do == "register"):
                try:
                    valid_data = JWTAuthentication().get_validated_token(token)
                    user = JWTAuthentication().get_user(valid_data)
                    data["uid"] = provider + "_" + data["uid"]
                except Exception as e:
                    data = {"token":token,"detail" : "Token not valid, Unauthorized", "except" : str(e)}
                    statusOut = status.HTTP_401_UNAUTHORIZED
                    return Response(data, status=statusOut)
                
                try: 
                    userSocial = SocialMediaAccount.objects.get(uid = data["uid"]).user
                    data = {"detail" : "Social media has already registered" if userSocial == user else "Social media account was taken"}
                    statusOut =  status.HTTP_208_ALREADY_REPORTED if userSocial == user else status.HTTP_403_FORBIDDEN
                except:
                    socmed = SocialMediaAccount(**data, user = user)
                    socmed.save()
                    data = SocialMediaAccountSerializer(socmed).data
            return Response(data, status=statusOut)
        except Exception as e:
            if(str(e) == "No SocialMediaAccount matches the given query."):
                return redirect("/login?state=error_msyacw&next=%s" % token)
            print("Error request : ", e)
            return redirect("/login?state=error_clwsa&next=%s" % token)
    
class OauthLogin(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def deliverData(self, request, provider, do):
        data = {"detail":"Provider does not support"}
        statusOut = status.HTTP_400_BAD_REQUEST

        if(do == "login"):
            token = request.query_params["next"] if "next" in request.query_params.keys() else "/"
        else:
            token = request.META["HTTP_AUTHORIZATION"].replace("STEP ", "")
        print("TOKEN :", token)
        if("google" in provider):
            data, _ = StaticOauthFlow.google(request, do, token).authorization_url(StaticOauthFlow.google_authorization_base_url,
                access_type="offline", prompt="select_account")
            print(data)
            if(".json" in provider):
                return Response(data)
            return redirect(data)
        elif("facebook" in provider):
            data, _ = StaticOauthFlow.facebook(request, do, token).authorization_url(StaticOauthFlow.facebook_authorization_base_url)
            print(data)
            if(".json" in provider):
                return Response(data)
            return redirect(data)
        elif("twitter" in provider):
            
            oauth = OAuth1(
                      settings.SOCIAL_AUTH_TWITTER_KEY, 
                      client_secret=settings.SOCIAL_AUTH_TWITTER_SECRET)
            data = urlencode({
                      "oauth_callback": reverse("oauth2-handler", request=request, kwargs={'do':do,'provider':"twitter"}).replace("http://","https://") + "?state=" + token
            })
            response = requests.post(StaticOauthFlow.twitter_token_url, auth=oauth, data=data)
            response.raise_for_status()
            response_split = response.text.split("&")
            oauth_token = response_split[0].split("=")[1]
            data = (
         f"https://api.twitter.com/oauth/authenticate?oauth_token={oauth_token}"
            )
            print(data)
            if(".json" in provider):
                return Response(data)
            else : return redirect(data)
        
        return Response(data, status= statusOut)

    def get(self, request, provider):
        return self.deliverData(request, provider, "login")

    def post(self, request, provider):
        return self.deliverData(request, provider, "register")