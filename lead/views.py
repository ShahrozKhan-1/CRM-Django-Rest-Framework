from rest_framework.response import Response
from user_auth.permissions import IsAdmin, IsManager, IsSales
from rest_framework.views import APIView
from .models import Lead
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from customer.models import Customer
from deal.models import Deal
from rest_framework import status
from django.db.models import Q




class LeadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsManager | IsSales]

    def get(self, request):
        user = request.user
        if user.roles == "Admin" or user.roles == "Manager":
            leads = Lead.objects.filter(is_deleted=False)

        else:
            leads = Lead.objects.filter(Q(created_by=request.user) | Q(assigned_to=request.user), is_deleted=False)
        serializer = LeadSerializer(leads, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"data":serializer.data, "message":"Lead Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, lead_id):
        lead = Lead.objects.get(id=lead_id, is_deleted=False)
        lead.is_deleted = True
        lead.save()
        return Response({"message":"Lead deleted successfully"})


class UserLeadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsManager | IsSales]

    def get(self, request):
        lead = Lead.objects.filter(assigned_to=request.user)
        serializer = LeadSerializer(lead, many=True)
        return Response({"data":serializer.data})
    
    def put(self, request, lead_id):
        if "status" in request.data:
            return Response({"Message":"Status can not be change"}, status=status.HTTP_400_BAD_REQUEST)
        lead = Lead.objects.get(id=lead_id, is_deleted=False)

        if request.user.roles == "Sales" and lead.assigned_to != request.user:
            return Response({"message":"You are not allowed to update the Lead"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LeadSerializer(lead, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"data":serializer.data, "message":"Lead Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LeadStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsManager | IsSales]

    def put(self, request, lead_id):
        lead = Lead.objects.get(id=lead_id, is_deleted=False)
        if request.user.roles == "Sales" and lead.assigned_to != request.user:
            return Response({"message": "You are not allowed to change this lead"}, status=status.HTTP_403_FORBIDDEN)
        serializer = LeadStatusSerializer(lead, data=request.data)
        if serializer.is_valid():
            lead = serializer.save(updated_by=request.user)

            if lead.status == Lead.STATUS.QUALIFIED and not Customer.objects.filter(lead=lead).exists():
                customer = Customer.objects.create(
                    name = lead.name,
                    email = lead.email,
                    phone = lead.phone,
                    company = lead.company,
                    assigned_to = lead.assigned_to,
                    lead = lead
                )
                Deal.objects.create(
                    title = lead.name,
                    assigned_to = lead.assigned_to,
                    customer = customer,
                    lead = lead
                )

                lead.status = Lead.STATUS.CONVERTED

            return Response({"data":serializer.data, "message":f"Lead Status Updated"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)