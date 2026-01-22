from rest_framework.response import Response
from user_auth.permissions import IsAdmin, IsManager, IsSales
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from deal.models import Deal
from rest_framework import status
from .serializers import *




class DealView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]


    def get(self, request):
        deal = Deal.objects.filter(is_deleted=False)
        serializer = DealSerializer(deal, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = DealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Deal Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        deal.is_deleted = True
        deal.save()
        return Response({"message":"Deal deleted successfully"})


class UserDealView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsSales | IsManager]

    def get(self, request):
        deal = Deal.objects.filter(assigned_to=request.user)
        serializer = DealSerializer(deal, many=True)
        return Response({"data":serializer.data})
    

    def put(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        if (request.user.roles == "Sales" and deal.assigned_to != request.user) or (deal.stage == Deal.STATUS.CLOSED and request.user.roles != "Admin"):
            return Response({"message":"You are not allowed to update the Deal"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DealSerializer(deal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Deal Updated Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DealStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsManager | IsSales]

    def put(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        if (request.user.roles == "Sales" and deal.assigned_to != request.user) or (deal.stage == Deal.STATUS.CLOSED and request.user.roles != "Admin"):
            return Response({"message": "You are not allowed to change this Deal"}, status=status.HTTP_403_FORBIDDEN)
        serializer = DealStageSerializer(deal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Deal Stage changed Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)