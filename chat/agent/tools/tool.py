from CRM.settings import TAVILY_API_KEY, vector_store
from langchain_tavily import TavilySearch
from bs4 import BeautifulSoup
from langchain.tools import tool
from urllib.request import Request, urlopen
from bs4.element import Comment
from .lead_tool import add_lead, edit_lead, search_leads
from .deal_tool import add_deal, edit_deal, search_deals


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
    return 



toolkit = [tavily_tool, get_web_content, search_uploaded_files, add_lead, edit_lead, search_leads, add_deal, edit_deal, search_deals]