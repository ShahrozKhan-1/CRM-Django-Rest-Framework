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

    def get(self, request):
        customer = Customer.objects.filter(is_deleted=False)
        serializer = CustomerSerializer(customer, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Customer Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, customer_id):
        customer = Customer.objects.get(id=customer_id, is_deleted=False)
        customer.is_deleted = True
        customer.save()
        return Response({"message":"Customer deleted successfully"})


class UserCustomerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "customer"

    def get(self, request):
        customer = Customer.objects.filter(assigned_to=request.user)
        serializer = CustomerSerializer(customer, many=True)
        return Response({"data":serializer.data})
    
    def put(self, request, customer_id):
        customer = Customer.objects.get(id=customer_id, is_deleted=False)
        
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Customer Updated Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
