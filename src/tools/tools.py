# python
import os
# 3rd party
from smolagents import tool
from AppOpener import open, close
@tool
def turn_of_pc(time: int = 5) -> None:
    """Tool for turning off the PC.
    Args:
        time (int): The time in seconds to turn off the PC.
    """
    os.system(f"shutdown /s /t {time}")

@tool
def reload_pc(time: int = 5) -> None:
    """Tool for reloading the PC.
    Args:
        time (int): The time in seconds to reload the PC.
    """
    os.system(f"shutdown /r /t {time}")

@tool
def open_app(app:str) -> None:
    """
    Tool for opening an application.
    Args:
        app (str): The name of the application to open.
    """
    try:
        open(app.lower())
    except Exception as e:
        print(f"Error opening {app}: {e}")

@tool
def close_app(app:str) -> None:
    """
    Tool for closing an application.
    Args:
        app (str): The name of the application to close.
    """
    try:
        close(app.lower())
    except Exception as e:
        print(f"Error closing {app}: {e}")
