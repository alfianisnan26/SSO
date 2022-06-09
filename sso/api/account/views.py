from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from sso.api.account.models import User
from sso.api.account.serializers import UserSerializer
from sso.lang.lang import Str

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        User.update(request)
        serializer = UserSerializer(request.user).data
        return Response(serializer)

    def post(self, request):
        User.update(request)
        pass

    def delete(self, request):
        User.update(request)
        pass