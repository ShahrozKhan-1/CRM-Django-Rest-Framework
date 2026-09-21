from CRM.settings import TAVILY_API_KEY, vector_store
from langchain_tavily import TavilySearch
from bs4 import BeautifulSoup
from langchain.tools import tool, ToolRuntime
from urllib.request import Request, urlopen
from bs4.element import Comment
from .lead_tool import add_lead, edit_lead, search_leads, get_lead_stats, convert_lead
from .deal_tool import add_deal, edit_deal, search_deals, get_deal_stats
from .customer_tool import add_customer, edit_customer, search_customer, get_customer_stats
from chat.agent.audit import log_agent_action, AgentActionLog
from chat.agent.context import AgentContext


@tool
def tavily_tool(content: str, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
    Search the web using Tavily based on the user's query.
    Args:
        content (str): The search query or topic to search for.
            Provide a clear, concise description of the information
            the user wants to find.
    Returns:
        The Tavily search tool configured for the given search topic.
    """
    current_user = runtime.context.user
    ctx = runtime.context
    input_data = {"content": content}
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

        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="tavily_tool",
            operation="read",
            entity_type="web",
            input_data=input_data,
            output_data={"count": len(results)},
            status=AgentActionLog.Status.SUCCESS,
            error_message="",
        )
        return str(results)
    except Exception as e:
        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="tavily_tool",
            operation="read",
            entity_type="web",
            input_data=input_data,
            status=AgentActionLog.Status.ERROR,
            error_message=str(e),
        )
        return f"Tavily search failed: {e}"


@tool
def get_web_content(url: str, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
        Fetch the webpage from the given URL and return its visible text.
        Args:
            content: containing the webpage URL.
        Returns:
            str: Visible text extracted from the webpage.
    """
    current_user = runtime.context.user
    ctx = runtime.context
    input_data = {"url": url}
    try:
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
        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="get_web_content",
            operation="read",
            entity_type="web",
            input_data=input_data,
            output_data={"content_length": len(visible_text)},
            status=AgentActionLog.Status.SUCCESS,
            error_message="",
        )
        return visible_text
    except Exception as e:
        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="get_web_content",
            operation="read",
            entity_type="web",
            input_data=input_data,
            status=AgentActionLog.Status.ERROR,
            error_message=str(e),
        )
        return f"Unable to fetch webpage content: {e}"


@tool
def search_uploaded_files(query: str, runtime: ToolRuntime[AgentContext] = None) -> str:
    """
    Search the uploaded files to find company-related information based on the user's query.

    Args:
        query (str): The search query or topic to look for in the uploaded documents.

    Returns:
        The most relevant content found in the uploaded files as object.
    """
    current_user = runtime.context.user
    ctx = runtime.context
    input_data = {"query": query}
    try:
        context = vector_store.similarity_search(query, k=4)
        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="search_uploaded_files",
            operation="read",
            entity_type="document",
            input_data=input_data,
            output_data={"count": len(context)},
            status=AgentActionLog.Status.SUCCESS,
            error_message="",
        )
        return context
    except Exception as e:
        log_agent_action(
            user=current_user,
            session_id=ctx.session_id,
            user_query=ctx.user_query,
            tool_name="search_uploaded_files",
            operation="read",
            entity_type="document",
            input_data=input_data,
            status=AgentActionLog.Status.ERROR,
            error_message=str(e),
        )
        return f"Unable to search uploaded files: {e}"



toolkit = [tavily_tool, get_web_content, search_uploaded_files, add_lead, edit_lead, search_leads, add_deal, edit_deal, search_deals, add_customer, edit_customer, search_customer, get_lead_stats, get_deal_stats, get_customer_stats, convert_lead]
