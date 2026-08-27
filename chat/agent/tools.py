from CRM.settings import TAVILY_API_KEY, vector_store
from langchain_tavily import TavilySearch
from langchain.tools import tool, ToolRuntime
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from bs4.element import Comment
from .schema import AddLead, EditLead
from lead.models import Lead
from lead.serializers import LeadSerializer
from user_auth.models import User
from .context import AgentContext
from django.db.models import Q


@tool
def tavily_tool(content:str) -> str:
    """
    Search the web using Tavily based on the user's query.
    Args:
        content (str): The search query or topic to search for.
            Provide a clear, concise description of the information
            the user wants to find.
    Returns:
        The Tavily search tool configured for the given search topic.
    """
    try:
        tavily_search_tool = TavilySearch(max_results=5, api_key=TAVILY_API_KEY)
        result = tavily_search_tool.invoke({"query":content})
        results = [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
            for item in result.get("results", [])
        ]

        return str(results)
    except Exception as e:
        return f"Tavily search failed: {e}"


@tool
def get_web_content(url:str) -> str:
    """
        Fetch the webpage from the given URL and return its visible text.
        Args:
            content: containing the webpage URL.
        Returns:
            str: Visible text extracted from the webpage.
    """
    print("got the response: ", url)
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            )
        },
    )
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    visible_text = " ".join(
        text.strip()
        for text in soup.find_all(string=True)
        if text.parent.name not in [
            "style", "script", "head", "title", "meta", "[document]"
        ]
        and not isinstance(text, Comment)
        and text.strip()
    )
    return visible_text


@tool
def search_uploaded_files(query: str) -> str:
    """
    Search the uploaded files to find company-related information based on the user's query.

    Args:
        query (str): The search query or topic to look for in the uploaded documents.

    Returns:
        The most relevant content found in the uploaded files as object.
    """
    context = vector_store.similarity_search(query, k=4)
    return context


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
    print("current user", current_user)
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
    The lead ID identifies the lead to update. Only the fields provided
    by the user will be changed.
    Args:
        id (int): ID of the lead to edit.
        name (str | None): Name of the lead.
        email (str | None): Email address of the lead.
        phone (str | None): Phone number of the lead.
        company (str | None): Company associated with the lead.
        source (str | None): Source from which the lead was acquired.
        description (str | None): Additional notes or description.
        assigned_to (str | None): Username of the user to assign the lead to.
    Returns:
        str: Confirmation message containing the updated lead details.
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



toolkit = [tavily_tool, get_web_content, search_uploaded_files, add_lead, edit_lead]
