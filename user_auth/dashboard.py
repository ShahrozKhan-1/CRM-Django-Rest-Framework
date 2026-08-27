from django.db.models.aggregates import Sum
from rest_framework.response import Response
from lead.models import Lead
from deal.models import Deal
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasPermissions
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Q



class DashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]

    def get(self, request):
        user = request.user

        return Response({
            "summary": get_dashboard_summary(user),
            "leads": get_lead_stats(user),
            "deals": get_deal_stats(user),
            "activity": get_dashboard_activity(user),

            "charts": {
                "leads_trend": get_leads_trend(user),
                "revenue_trend": get_revenue_trend(user),
                "deals_by_stage": get_deals_by_stage(user),
            }
        })


def get_dashboard_leads_queryset(user):
    queryset = Lead.objects.filter(is_deleted=False)
    if user.is_superuser:
        return queryset
    return queryset.filter(Q(assigned_to=user) | Q(created_by=user))


def get_dashboard_deals_queryset(user):
    queryset = Deal.objects.filter(is_deleted=False)
    if user.is_superuser:
        return queryset
    return queryset.filter(assigned_to=user)


def get_dashboard_summary(user):
    lead_queryset = get_dashboard_leads_queryset(user)
    deal_queryset = get_dashboard_deals_queryset(user)

    total_leads = lead_queryset.count()
    open_deals = deal_queryset.filter(stage=Deal.STATUS.OPEN)
    closed_deals = deal_queryset.filter(stage=Deal.STATUS.CLOSED)
    total_deals = deal_queryset.count()

    pipeline_value = open_deals.aggregate(total=Sum('amount'))['total'] or 0
    won_revenue = closed_deals.aggregate(total=Sum('amount'))['total'] or 0

    return {
        "total_leads": total_leads,
        "total_deals": total_deals,
        "open_deals": open_deals.count(),
        "closed_deals": closed_deals.count(),
        "pipeline_value": pipeline_value,
        "won_revenue": won_revenue,
    }



def get_lead_stats(user):
    queryset = get_dashboard_leads_queryset(user)

    return {
        "new": queryset.filter(status=Lead.STATUS.NEW).count(),
        "contacted": queryset.filter(status=Lead.STATUS.CONTACTED).count(),
        "qualified": queryset.filter(status=Lead.STATUS.QUALIFIED).count(),
        "converted": queryset.filter(status=Lead.STATUS.CONVERTED).count(),
        "lost": queryset.filter(status=Lead.STATUS.CLOSED_LOST).count(),
    }


def get_deal_stats(user):
    queryset = get_dashboard_deals_queryset(user)

    return {
        "open": queryset.filter(stage=Deal.STATUS.OPEN).count(),
        "won": queryset.filter(stage=Deal.STATUS.WON).count(),
        "lost": queryset.filter(stage=Deal.STATUS.LOST).count(),
        "closed": queryset.filter(stage=Deal.STATUS.CLOSED).count(),
    }


def get_dashboard_activity(user):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    lead_queryset = get_dashboard_leads_queryset(user)
    deal_queryset = get_dashboard_deals_queryset(user)

    return {
        "leads_today": lead_queryset.filter(created_at__gte=today_start).count(),
        "deals_today": deal_queryset.filter(created_at__gte=today_start).count(),
        "leads_this_week": lead_queryset.filter(created_at__gte=week_start).count(),
        "deals_this_week": deal_queryset.filter(created_at__gte=week_start).count(),
    }

def get_leads_trend(user, days=30):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    queryset = get_dashboard_leads_queryset(user).filter(created_at__gte=start_date)

    data = (
        queryset
        .values('created_at__date')
        .annotate(count=Count('id'))
        .order_by('created_at__date')
    )
    return [
        {
            "date": item["created_at__date"],
            "count": item["count"]
        }
        for item in data
    ]


def get_revenue_trend(user):
    queryset = get_dashboard_deals_queryset(user).filter(stage=Deal.STATUS.CLOSED)

    data = (
        queryset
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(revenue=Sum('amount'))
        .order_by('month')
    )
    return [
        {
            "month": item["month"].strftime("%Y-%m"),
            "revenue": item["revenue"] or 0
        }
        for item in data
    ]


def get_deals_by_stage(user):
    queryset = get_dashboard_deals_queryset(user)

    data = (queryset
        .values('stage')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return [
        {
            "stage": item["stage"],
            "count": item["count"]
        }
        for item in data
    ]
