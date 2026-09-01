from rest_framework.response import Response
from user_auth.permissions import HasPermissions
from rest_framework.views import APIView
from .models import Lead
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from customer.models import Customer
from rest_framework import status
from .serializers import *




class CustomerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "customer"


    def get_queryset(self):
        user = self.request.user
        queryset = Customer.objects.filter(is_deleted=False)
        if user.is_superuser:
            return queryset
        role_name = user.roles.name.lower() if user.roles else None
        if role_name == "admin":
            return queryset
        if role_name == "manager":
            return queryset.filter(lead__created_by=user)
        if role_name == "sale":
            return queryset.filter(assigned_to=user)
        return queryset.none()

    def get(self, request, customer_id=None):
        queryset = self.get_queryset()
        if customer_id:
            customer = queryset.filter(id=customer_id).first()
            serializer = CustomerSerializer(customer)
            return Response({"data":serializer.data})
        customers = queryset
        serializer = CustomerSerializer(customers, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Customer Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, customer_id):
        queryset = self.get_queryset()
        customer = queryset.filter(id=customer_id).first()
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Customer Updated Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, customer_id):
        queryset = self.get_queryset()
        customer = queryset.filter(id=customer_id).first()
        customer.is_deleted = True
        customer.save()
        return Response({"message":"Customer deleted successfully"})
