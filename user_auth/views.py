from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .permissions import *
from lead.models import Lead
from lead.serializers import LimitedLeadSerializer
from deal.models import Deal
from deal.serializers import LimitedDealSerializer
from customer.models import Customer
from customer.serializers import LimitedCustomerSerailizer
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination
from .models import Role, Permission


User = get_user_model()

class CreateUser(APIView):
    permission_classes = [HasPermissions]
    authentication_classes = [JWTAuthentication]
    permission_name = "user"

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"data":serializer.data})
    

    def post(self, request):
        instance = request.data
        if 'roles' not in instance:
            return Response({"message":"Role is not defined for the user"})
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Created Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Creating User"}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, user_id):
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Edited Succesfully"})
        return Response({"message":serializer.errors})
    

class UserProfile(APIView):

    permission_classes = [HasPermissions]
    authentication_classes = [JWTAuthentication]
    permission_name = "user"

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response({"data":serializer.data})
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Edited Succesfully"})
        return Response({"message":serializer.errors})


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]



class RolesView(APIView):
    permission_classes = [HasPermissions]
    authentication_classes = [JWTAuthentication]
    permission_name = "user"

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response({"data":serializer.data})
    

    def post(self, request):
        instance = request.data
        serializer = RoleSerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Role Created Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Creating Role"})
    
    def put(self, request, role_id):
        role = Role.objects.get(id=role_id)
        serializer = RoleSerializer(role, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Role Edited Succesfully"})
        return Response({"message":serializer.errors})
    
    def delete(self, request, role_id):
        role = Deal.objects.get(id=role_id, is_deleted=False)
        role.is_deleted = True
        role.save()
        return Response({"message":"Role deleted successfully"})


class PermissionView(APIView):
    permission_classes = [HasPermissions]
    authentication_classes = [JWTAuthentication]
    permission_name = "user"

    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response({"data":serializer.data})

    def post(self, request):
        instance = request.data
        print("permission actions list: ", instance.get("actions"))
        serializer = PermissionSerializer(data=instance)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Permission Created Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Creating Permission"})
    
    def put(self, request, permission_id):
        permission = Permission.objects.get(id=permission_id)
        serializer = PermissionSerializer(permission, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"User Edited Succesfully"})
        return Response({"message":serializer.errors})
    
    def delete(self, request, permission_id):
        permission = Permission.objects.get(id=permission_id)
        permission.delete()
        return Response({"message":"permission deleted successfully"})


class SearchAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "search"

    def get(self, request):
        query = request.GET.get('q', '').strip()

        if not query:
            return Response(
                {"error": "Please provide a search query"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Queries
        leads = Lead.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query)
        )

        deals = Deal.objects.filter(
            Q(title__icontains=query) |
            Q(stage__icontains=query)
        )

        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query)
        )


        # Merge results
        results = (
            list(LimitedLeadSerializer(leads, many=True).data) +
            list(LimitedDealSerializer(deals, many=True).data) +
            list(LimitedCustomerSerailizer(customers, many=True).data)
        )

        paginator = LimitOffsetPagination()
        paginated_results = paginator.paginate_queryset(results, request)

        return paginator.get_paginated_response({
            "query": query,
            "results": paginated_results
        })
