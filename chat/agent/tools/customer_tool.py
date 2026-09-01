from langchain.tools import tool, ToolRuntime
from chat.agent.schema import *
from customer.serializers import CustomerSerializer
from chat.agent.context import AgentContext
from customer.models import Customer


@tool
def add_customer(customer: AddCustomer, runtime: ToolRuntime[AgentContext]) -> str:
    """
    Create a new customer in the CRM.
    Customers can be created independently when the user explicitly requests
    a new customer. A customer may also be created automatically by the CRM
    when an existing lead's status is changed to "Qualified".
    Use this tool only when the user explicitly wants to create a customer
    directly. Do not use this tool to convert a lead. Lead conversion is
    handled automatically by the CRM when the lead status becomes "Qualified".
    Customer fields:
    - name: Name of the customer.
    - email: Email address of the customer.
    - phone: Phone number of the customer.
    - company: Company associated with the customer.
    - lead: Optional ID of the lead from which this customer originated.
      Provide this only when the customer should be associated with an
      existing lead.
    - assigned_to: ID of the CRM user who should be assigned to the customer.
      This field is required when creating a customer.
    If the user refers to a lead by name or other information instead of
    providing its ID, use the appropriate lead-search tool first to resolve
    the correct lead ID. Do not invent or assume lead IDs.
    If the user specifies a CRM user by name, username, or other information
    instead of providing the user's ID, use the appropriate user-search tool
    first to resolve the correct user ID. Do not invent or assume user IDs.
    Args:
        customer (AddCustomer):
            Customer information required to create the customer.

        runtime (ToolRuntime[AgentContext]):
            Agent runtime containing the currently authenticated CRM user.
    Returns:
        str:
            A confirmation message containing the created customer's name
            and ID, or validation errors if the customer could not be created.
    """

    current_user = runtime.context.user

    customer_data = {
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "company": customer.company,
        "lead": customer.lead,
        "assigned_to": customer.assigned_to,
    }

    serializer = CustomerSerializer(data=customer_data)

    if serializer.is_valid():
        instance = serializer.save()

        return (
            f"Customer '{instance.name}' was successfully created "
            f"with ID {instance.id}."
        )

    return f"Unable to create customer: {serializer.errors}"


@tool
def edit_customer(
    customer: EditCustomer,
    runtime: ToolRuntime[AgentContext] = None,
) -> str:
    """
    Edit an existing customer in the CRM.
    Use this tool when the user wants to modify information about an existing
    customer. The `id` field is required to identify which customer should
    be updated.
    Customers may have been created either:
    1. Directly through the customer creation workflow.
    2. Automatically through the lead-conversion workflow when a lead's
       status was changed to "Qualified".
    Only update fields that the user explicitly requests. Do not modify or
    overwrite fields that were not provided.
    Editable fields:
    - id: ID of the customer to edit. Required.
    - name: New name of the customer.
    - email: New email address of the customer.
    - phone: New phone number of the customer.
    - company: New company associated with the customer.
    - lead: ID of the lead to associate with the customer.
    - assigned_to: ID of the CRM user to assign the customer to.
    If the user wants to edit a customer but does not provide the customer ID,
    use `search_customer` first to find the correct customer and obtain its ID.
    If the user wants to associate the customer with a lead but refers to the
    lead by name or other information instead of ID, use the appropriate
    lead-search tool first to resolve the lead ID.
    If the user wants to assign the customer to another CRM user but provides
    a name, username, or other information instead of a user ID, use the
    appropriate user-search tool first to resolve the user's ID.
    Do not invent or assume customer, lead, or user IDs.
    Returns:
        str:
            A confirmation message containing the updated customer's name
            and ID, or an error message if the customer cannot be found,
            accessed, or updated.
    """

    current_user = runtime.context.user
    try:
        instance = Customer.objects.get(assigned_to=current_user, id=customer.id)
    except Customer.DoesNotExist:
        return f"Customer with ID {customer.id} was not found or you don't have permission to edit it."
    data = {}
    if customer.name is not None:
        data["name"] = customer.name

    if customer.email is not None:
        data["email"] = customer.email

    if customer.phone is not None:
        data["phone"] = customer.phone

    if customer.company is not None:
        data["company"] = customer.company

    if customer.lead is not None:
        data["lead"] = customer.lead

    if customer.assigned_to is not None:
        data["assigned_to"] = customer.assigned_to

    serializer = CustomerSerializer(
        instance=instance,
        data=data,
        partial=True,
    )
    if serializer.is_valid():
        instance = serializer.save()
        return (
            f"Customer '{instance.name}' was successfully updated "
            f"with ID {instance.id}."
        )

    return f"Unable to update Customer: {serializer.errors}"


@tool
def search_customer(customer: SearchCustomer, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
    Search for existing customers in the CRM.
    Use this tool when the user wants to find, view, identify, or obtain the
    ID of an existing customer. It should also be used before `edit_customer`
    when the user identifies a customer by name or other information instead
    of providing the customer ID.
    Customers may have been created either directly or automatically through
    the lead-conversion workflow when a lead's status was changed to
    "Qualified".
    Customers can be searched or filtered using:
    - name: Customer name.
    - email: Customer email address.
    - phone: Customer phone number.
    - company: Company name associated with the customer.
    - lead: ID of the lead associated with the customer.
    - assigned_to: ID of the CRM user assigned to the customer.
    Multiple provided fields should be used together to narrow the search and
    identify the most relevant customer.
    If the user refers to an associated lead by name instead of its ID, use
    the appropriate lead-search tool first to resolve the lead ID before
    filtering customers by lead.
    If the user refers to an assigned CRM user by name or username instead of
    their ID, use the appropriate user-search tool first to resolve the user ID
    before filtering customers by `assigned_to`.
    The search results should include customer IDs so that the correct ID can
    be passed to tools such as `edit_customer`.
    Do not use this tool to create, edit, delete, or otherwise modify customers.
    Do not invent customer, lead, or user IDs.
    Returns:
        str:
            Matching customer details including their IDs, or a message if
            no matching customers are found.
    """

    current_user = runtime.context.user
    print("request: ", customer)
    try:
        queryset = Customer.objects.filter(
            assigned_to=current_user,
            is_deleted=False
        )
        print("initial:", list(queryset))

        if customer.name:
            queryset = queryset.filter(name__icontains=customer.name)
            print("after name:", list(queryset))

        if customer.email:
            queryset = queryset.filter(email__iexact=customer.email)
            print("after email:", list(queryset))

        if customer.phone:
            queryset = queryset.filter(phone=customer.phone)
            print("after phone:", list(queryset))

        if customer.company:
            queryset = queryset.filter(company__icontains=customer.company)
            print("after company:", list(queryset))

        if customer.lead:
            queryset = queryset.filter(lead_id=customer.lead)
            print("after lead:", list(queryset))

        if customer.assigned_to:
            queryset = queryset.filter(assigned_to_id=customer.assigned_to)
            print("after assigned_to:", list(queryset))
        customers = queryset[:10]
        print("final searched customer: ", customers)
        if not customers:
            return "No matching customers were found."
        return "\n".join(
            [
                f"Id: {item.id}"
                f"Name: {item.name}, "
                f"Email: {item.email}, "
                f"Phone Number: {item.phone}, "
                f"Company: {item.company}, "
                f"Lead: {item.lead}, "
                f"Assigned to: {item.assigned_to}, "
                for item in customers
            ]
        )
    except Exception as e:
        return f"Unable to search customers: {str(e)}"

