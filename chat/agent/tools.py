from CRM.settings import TAVILY_API_KEY
from langchain_tavily import TavilySearch
from langchain.tools import tool
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from bs4.element import Comment

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

toolkit = [tavily_tool, get_web_content]
    