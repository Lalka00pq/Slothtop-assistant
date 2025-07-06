# python
import os
# 3rd party
from AppOpener import open as open_app, close
from langchain.tools import tool


@tool
def turn_off_pc_tool(time: int = 5) -> None:
    """Tool for shutting down the PC.

    Args:
        time (int, optional): The time in seconds to wait before shutting down. Defaults to 5.
    """
    os.system(f"shutdown /s /t {time}")


@tool
def restart_pc_tool(time: int = 5) -> None:
    """Tool for restarting the PC.

    Args:
        time (int, optional): The time in seconds to wait before restarting. Defaults to 5.
    """
    os.system(f"shutdown /r /t {time}")


@tool
def open_app_tool(app: str) -> None:
    """Tool for opening a computer application.

    Args:
        app (str): The name of the application to open.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        open_app(app.lower())
        print(f'{app} opened successfully.')
    except Exception as e:
        print(f"Error opening {app}: {e}")


@tool
def close_app_tool(app: str) -> None:
    """Tool for closing an application.

    Args:
        app (str): The name of the application to close.
    """
    try:
        close(app.lower())
    except Exception as e:
        print(f"Error closing {app}: {e}")
