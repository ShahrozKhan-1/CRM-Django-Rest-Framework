from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .permissions import IsAdmin



User = get_user_model()

class CreateUser(APIView):
    permission_classes = [IsAdminUser | IsAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        instance = request.data
        if 'roles' not in instance:
            return Response({"message":"Role is not defined for the user"})
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Created Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Creating User"})
    
    def put(self, request, user_id):
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Edited Succesfully"})
        return Response({"message":serializer.errors})


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer