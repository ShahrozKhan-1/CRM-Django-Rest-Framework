from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
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
from attachment.models import Attachment
from attachment.serializers import AttachmentSerializer
from rest_framework import status
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination


User = get_user_model()

class CreateUser(APIView):
    permission_classes = [IsAdminUser | IsAdmin]
    authentication_classes = [JWTAuthentication]

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

class SearchAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSales | IsManager]

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

        attachments = Attachment.objects.filter(name__icontains=query)

        # Merge results
        results = (
            list(LimitedLeadSerializer(leads, many=True).data) +
            list(LimitedDealSerializer(deals, many=True).data) +
            list(LimitedCustomerSerailizer(customers, many=True).data) +
            list(AttachmentSerializer(attachments, many=True).data)
        )

        paginator = LimitOffsetPagination()
        paginated_results = paginator.paginate_queryset(results, request)

        return paginator.get_paginated_response({
            "query": query,
            "results": paginated_results
        })
