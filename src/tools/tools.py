# python
import os
# 3rd party
from AppOpener import open as open_app, close
from langchain.tools import tool
import webbrowser


@tool
def turn_off_pc_tool(time: int = 5) -> str:
    """Tool for shutting down the PC.

    Args:
        time (int, optional): The time in seconds to wait before shutting down. Defaults to 5.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        os.system(f"shutdown /s /t {time}")
        return f"PC will shut down in {time} seconds."
    except Exception as e:
        return f"Error shutting down PC: {e}"


@tool
def restart_pc_tool(time: int = 5) -> str:
    """Tool for restarting the PC.

    Args:
        time (int, optional): The time in seconds to wait before restarting. Defaults to 5.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        os.system(f"shutdown /r /t {time}")
        return f"PC will restart in {time} seconds."
    except Exception as e:
        return f"Error restarting PC: {e}"


@tool
def open_app_tool(app: str) -> str:
    """Tool for opening a computer application.

    Args:
        app (str): The name of the application to open.
    Returns:
        str: A message indicating the result of the operation.
    """

    try:
        open_app(app.lower())
        return f'{app} opened successfully.'
    except Exception as e:
        return f"Error opening {app}: {e}"


@tool
def close_app_tool(app: str) -> str:
    """Tool for closing an application.

    Args:
        app (str): The name of the application to close.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        close(app.lower())
        return f'{app} closed successfully.'
    except Exception as e:
        return f"Error closing {app}: {e}"


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
def deep_web_search_tool(query: str) -> str:
    """Tool for performing a deep web search.

    Args:
        query (str): The search query.
    Returns:
        str: A message indicating the result of the operation.
    """
    ...
