from http import client
import mimetypes
import os
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
import random
from http.cookies import SimpleCookie
from oauth2_provider.models import Application
from sso.api.account.models import User

from sso.api.res.serializers import BackroundSerializer
from .models import Background
from django.conf import settings
class BackgroundView(APIView):
    def get(self, request):
        User.update(request)
        try:
            if(not request.COOKIES.get("bg_uuid")):
                bg = Background.objects.filter(is_active=True)
                if(not bg.exists()):
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                bg = random.sample(list(bg), 1)[0]
                resp = HttpResponse(bg.image, content_type="image/jpeg")
                try:
                    expires = request.query_params["e"]
                except:
                    expires = 10
                resp.set_cookie('bg_uuid',str(bg.uuid),expires=expires)
            else:
                bg = get_object_or_404(Background, pk=request.COOKIES.get("bg_uuid"))
                resp = HttpResponse(bg.image, content_type="image/jpeg")
            return resp
        except Exception as e:
            print("Error from bg :", e)
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

class BackgroundInfoView(APIView):
    def get(self, request):
        User.update(request)
        if(request.COOKIES.get("bg_uuid")):
            bg = get_object_or_404(Background, pk=request.COOKIES.get("bg_uuid"))
            serializer = BackroundSerializer(bg)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        