# 3rd party
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


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
