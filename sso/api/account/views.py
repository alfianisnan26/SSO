from rest_framework.views import APIView

from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from sso.auths.utils import UserLoginData

from sso.api.account.utils import MAIN_DOMAIN

class TokenObtainPairView(APIView):
    def post(self, request):

        uld = UserLoginData(request)

        if(uld.validate()):
            user = uld.authenticate()
            if(uld.validate()):
                return Response({'detail': str(user)})
        return Response({"error": uld.error}, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass

    def delete(self, request):
        pass

    def patch(self, request):
        pass