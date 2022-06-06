from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from sso.api.account.models import User
from sso.api.account.serializers import UserSerializer
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

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user).data
        return Response(serializer)

    def post(self, request):
        pass

    def delete(self, request):
        pass

    def patch(self, request):
        pass