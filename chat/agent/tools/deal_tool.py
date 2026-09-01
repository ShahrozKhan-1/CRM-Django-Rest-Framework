from langchain.tools import tool, ToolRuntime
from chat.agent.schema import *
from deal.serializers import DealSerializer
from chat.agent.context import AgentContext
from deal.models import Deal
from django.db.models import Q



def get_deal_queryset(user): 
    queryset = Deal.objects.filter(is_deleted=False) 
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


@tool
def add_deal(deal: AddDeal, runtime: ToolRuntime[AgentContext]) -> str:
    """
    Create a new deal in the CRM.
    The tool creates a deal using the provided deal information and assigns
    it to the currently authenticated user from the agent runtime context.
    The customer must be provided as a valid customer ID. A lead ID may also
    be provided when the deal is associated with an existing lead.
    Args:
        deal (AddDeal): Details required to create the deal, including title,
            amount, stage, expected close date, description, customer ID,
            and optional lead ID.

        runtime (ToolRuntime[AgentContext]): Agent runtime containing the
            currently authenticated CRM user.
    Returns:
        str: A confirmation message containing the created deal's title and ID,
        or validation errors if the deal could not be created.
    """

    current_user = runtime.context.user

    deal_data = {
        "title": deal.title,
        "amount": deal.amount,
        "stage": deal.stage,
        "expected_close_date": deal.expected_close_date,
        "description": deal.description,
        "customer": deal.customer,
        "assigned_to": current_user.id,
        "lead": deal.lead,
    }

    serializer = DealSerializer(data=deal_data)

    if serializer.is_valid():
        instance = serializer.save()

        return (
            f"Deal '{instance.title}' was successfully created "
            f"with ID {instance.id}."
        )

    return f"Unable to create deal: {serializer.errors}"


@tool
def edit_deal(
    deal: EditDeal,
    runtime: ToolRuntime[AgentContext] = None,
) -> str:
    """
        Edit an existing Deal in the CRM.
        Use this tool when the user wants to modify information about an existing
        deal. The `id` field identifies the deal that should be updated.
        Only modify fields that the user explicitly provides. Do not change or
        overwrite fields that were not requested.

        Editable fields:
        - id: ID of the deal to edit. This is required to identify the deal.
        - title: Title or name of the deal.
        - amount: Monetary amount of the deal.
        - stage: Current stage of the deal.
        - expected_close_date: Expected closing date of the deal.
        - description: Additional notes or description about the deal.
        - customer: ID of the customer associated with the deal.
        - lead: ID of the lead associated with the deal, if applicable.

        Valid deal stages are:
        - Open: The deal is currently active and being pursued.
        - Won: The deal has been successfully completed.
        - Lost: The deal was not successfully completed.
        - Closed: The deal has been closed.
        Only change the deal stage when the user explicitly requests it or clearly
        indicates that the deal should move to another stage.

        Use the appropriate deal-search/get tool first to identify the correct deal
        and obtain its ID before calling this tool.
        Do not invent IDs or assume an ID from a name without first resolving it
        through the appropriate CRM lookup tool.

        Returns:
            str: A confirmation message containing the updated deal title and ID,
            or an error message if the deal cannot be found.
    """

    current_user = runtime.context.user
    try:
        instance = get_deal_queryset(current_user).filter(id=deal.id).first()
    except Deal.DoesNotExist:
        return f"Deal with ID {deal.id} was not found or you don't have permission to edit it."
    data = {}
    if deal.title is not None:
        data["title"] = deal.title

    if deal.amount is not None:
        data["amount"] = deal.amount

    if deal.stage is not None:
        data["stage"] = deal.stage

    if deal.expected_close_date is not None:
        data["expected_close_date"] = deal.expected_close_date

    if deal.customer is not None:
        data["customer"] = deal.customer

    if deal.description is not None:
        data["description"] = deal.description

    if deal.lead is not None:
        data["lead"] = deal.lead

    serializer = DealSerializer(
        instance=instance,
        data=data,
        partial=True,
    )
    if serializer.is_valid():
        instance = serializer.save()
        return (
            f"Deal '{instance.title}' was successfully updated "
            f"with ID {instance.id}."
        )

    return f"Unable to update deal: {serializer.errors}"


@tool
def search_deals(deal: SearchDeal, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
    Search for existing deals in the CRM.
    Use this tool to find deals by title, amount, expected close date,
    customer, lead, or stage. Returns matching deals with their IDs.
    Valid stages:
    - Open
    - Won
    - Lost
    - Closed

    If the user wants to edit a deal but does not provide its ID,
    search for the deal first and use the returned ID with edit_deal.
    Do not use this tool to modify deals.
    Returns:
        Matching deal details with their IDs, or a message if no deals are found.
    """

    current_user = runtime.context.user
    try:
        queryset = get_deal_queryset(current_user)
        if deal.title:
            queryset = queryset.filter(title__icontains=deal.title)
        if deal.amount:
            queryset = queryset.filter(amount__iexact=deal.amount)
        if deal.expected_close_date:
            queryset = queryset.filter(expected_close_date=deal.expected_close_date)
        if deal.customer:
            queryset = queryset.filter(customer__name__icontains=deal.customer)
        if deal.lead:
            queryset = queryset.filter(lead_id=deal.lead)
        if deal.stage:
            queryset = queryset.filter(stage__iexact=deal.stage)
        deals = queryset[:10]
        if not deals:
            return "No matching deals were found."
        return "\n".join(
            [
                f"Id: {item.id}"
                f"Title: {item.title}, "
                f"Amount: {item.amount}, "
                f"Expected Close Date: {item.expected_close_date}, "
                f"Customer: {item.customer}, "
                f"Stage: {item.stage}"
                for item in deals
            ]
        )
    except Exception as e:
        return f"Unable to search deals: {str(e)}"
