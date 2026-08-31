from langchain.tools import tool, ToolRuntime
from chat.agent.schema import *
from lead.models import Lead
from lead.serializers import LeadSerializer
from user_auth.models import User
from chat.agent.context import AgentContext
from django.db.models import Q


@tool
def add_lead(lead:AddLead, runtime: ToolRuntime[AgentContext] = None,) -> str:
    """
    Add a new lead to the CRM database using the provided lead details.

    Args:
        name (str): Name of the lead.
        email (str): Email address of the lead.
        phone (str | None): Phone number of the lead.
        company (str | None): Company associated with the lead.
        source (str | None): Source from which the lead was acquired.
        description (str | None): Additional notes or description about the lead.
        assigned_to (str | None): Name of the user to whom the lead should be assigned.

    Returns:
        str: Confirmation message containing the details of the newly created lead.
    """
    current_user = runtime.context.user
    try:
        assigned_user = User.objects.get(username=lead.assigned_to)
    except Exception as e:
        return f"Problem while finding user: {e}"
    lead = {
        "name":lead.name,
        "email":lead.email,
        "phone":lead.phone,
        "company":lead.company,
        "source":lead.source,
        "description":lead.description,
        "assigned_to":assigned_user.id
    }
    serializer = LeadSerializer(data=lead)
    if serializer.is_valid():
        instance = serializer.save(created_by=current_user)
        return (
            f"Lead '{instance.name}' was successfully created "
            f"with ID {instance.id}."
        )
    return f"Unable to create lead: {serializer.errors}"


@tool
def edit_lead(
    lead: EditLead,
    runtime: ToolRuntime[AgentContext] = None,
) -> str:
    """
    Edit an existing lead in the CRM database.

    Use this tool when the user wants to modify information
    about an existing lead. The lead ID identifies the lead
    to update. Only fields explicitly provided by the user
    should be changed; do not modify unspecified fields.

    The lead status can be changed using the LeadStatus enum.
    Valid statuses are:

    - New: The lead has been created but has not been contacted.
    - Contacted: The lead has been contacted.
    - Qualified: The lead has been evaluated and is a qualified opportunity.
    - Converted: The lead has successfully converted into a customer.
    - Closed_Lost: The lead is no longer expected to convert.

    Status should only be changed when the user explicitly
    requests a status change or clearly indicates that the
    lead should move to another status.

    Editable fields:
    - id: ID of the lead to edit.
    - name: Name of the lead.
    - email: Email address of the lead.
    - phone: Phone number of the lead.
    - company: Company associated with the lead.
    - source: Source from which the lead was acquired.
    - status: Current status of the lead.
    - description: Additional notes or description.
    - assigned_to: Username of the user to assign the lead to.

    Returns:
        A confirmation message containing the updated lead details.
    """

    current_user = runtime.context.user
    try:
        instance = Lead.objects.get(
            Q(assigned_to=current_user) | Q(created_by=current_user),
            id=lead.id,
        )
    except Lead.DoesNotExist:
        return f"Lead with ID {lead.id} was not found or you don't have permission to edit it."
    data = {}
    if lead.name is not None:
        data["name"] = lead.name

    if lead.email is not None:
        data["email"] = lead.email

    if lead.phone is not None:
        data["phone"] = lead.phone

    if lead.company is not None:
        data["company"] = lead.company

    if lead.source is not None:
        data["source"] = lead.source

    if lead.status is not None:
        data["status"] = lead.status

    if lead.description is not None:
        data["description"] = lead.description

    if lead.assigned_to is not None:
        try:
            assigned_user = User.objects.get(
                username=lead.assigned_to
            )
            data["assigned_to"] = assigned_user.id

        except User.DoesNotExist:
            return (
                f"User '{lead.assigned_to}' does not exist."
            )
    serializer = LeadSerializer(
        instance=instance,
        data=data,
        partial=True,
    )
    if serializer.is_valid():
        instance = serializer.save()
        return (
            f"Lead '{instance.name}' was successfully updated "
            f"with ID {instance.id}."
        )

    return f"Unable to update lead: {serializer.errors}"


@tool
def search_leads(lead: SearchLead, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
    Search for existing leads in the CRM database.
    Use this tool to find leads by name, email, phone, company,
    source, or status. The tool returns matching leads with their IDs.
    If the user wants to edit a lead but does not provide its ID,
    search for the lead first and use the returned ID with edit_lead.
    Valid statuses:
    - New: Lead has not been contacted.
    - Contacted: Lead has been contacted but not qualified.
    - Qualified: Lead meets the criteria for a potential customer.
    - Converted: Lead has become a customer.
    - Closed_Lost: Lead will not convert.
    Do not use this tool to modify leads.
    Returns:
        Matching lead details with their IDs, or a message if no
        matching leads are found.
    """

    current_user = runtime.context.user
    try:
        queryset = Lead.objects.filter(Q(assigned_to=current_user) | Q(created_by=current_user), is_deleted=False)
        if lead.name:
            queryset = queryset.filter(name__icontains=lead.name)
        if lead.email:
            queryset = queryset.filter(email__iexact=lead.email)
        if lead.phone:
            queryset = queryset.filter(phone=lead.phone)
        if lead.company:
            queryset = queryset.filter(company__icontains=lead.company)
        if lead.source:
            queryset = queryset.filter(source__iexact=lead.source)
        if lead.status:
            queryset = queryset.filter(status__iexact=lead.status)
        leads = queryset[:10]
        if not leads:
            return "No matching leads were found."
        return "\n".join(
            [
                f"Id: {item.id}"
                f"Name: {item.name}, "
                f"Email: {item.email}, "
                f"Phone: {item.phone}, "
                f"Company: {item.company}, "
                f"Source: {item.source}"
                for item in leads
            ]
        )
    except Exception as e:
        return f"Unable to search leads: {str(e)}"