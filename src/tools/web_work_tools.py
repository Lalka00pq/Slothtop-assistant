import os
from dotenv import load_dotenv
# 3rd party
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_tavily import TavilySearch
import webbrowser

load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')


@tool
def search_web_tool(query: str) -> str:
    """Tools for search the web for a given query.

    Args:
        query (str): The search query.

    Returns:
        str: The search results.
    """
    search = DuckDuckGoSearchRun()
    result = search.run(query)
    return result


@tool
def make_a_web_search_tool(query: str) -> str:
    """Tool for performing a web search.

    Args:
        query (str): The search query.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for '{query}' on Google."
    except Exception as e:
        return f"Error performing web search: {e}"


@tool
def tavily_web_search_tool(query: str) -> str:
    """Tool for performing a deep web search.

    Args:
        query (str): The search query.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        search = TavilySearch(

        )
        result = search.run(query)
        return result
    except Exception as e:
        return f"Error performing deep web search: {e}"
