from rest_framework.response import Response
from lead.models import Lead
from deal.models import Deal
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import *



class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]


    def get(self, request):
        user = request.user

        lead_count = 0
        open_deal_count = 0
        close_deal_count = 0
        if user.roles == 'Admin' or user.roles == 'Manager':
            lead_count = Lead.objects.filter(is_deleted=False).count()
            open_deal_count = Deal.objects.filter(is_deleted=False, stage='Open').count()
            close_deal_count = Deal.objects.filter(is_deleted=False, stage='Close').count()

        if user.roles == 'Sales':
            lead_count = Lead.objects.filter(is_deleted=False, assigned_to=user).count()
            open_deal_count = Deal.objects.filter(is_deleted=False, stage='Open', assigned_to=user).count()
            close_deal_count = Deal.objects.filter(is_deleted=False, stage='Close', assigned_to=user).count()
        
        return Response({
            "lead_count":lead_count,
            "open_deal_count":open_deal_count,
            "close_deal_count":close_deal_count,
        })
