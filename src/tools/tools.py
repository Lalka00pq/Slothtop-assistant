# python
import os
import requests
# 3rd party
from AppOpener import open as open_app, close as close_app
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")


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
        open_app(app.lower(), match_closest=True, throw_error=True)
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
        close_app(app.lower(), match_closest=True, throw_error=True)
        return f'{app} closed successfully.'
    except Exception as e:
        return f"Error closing {app}: {e}"


@tool
def get_weather_tool(location: str) -> str:
    """Tool for getting the weather information.

    Args:
        location (str): The location to get the weather for.
    Returns:
        str: A message indicating the result of the operation.
    """
    try:
        headers = {
            "accept": "application/json"
        }
        response = requests.get(
            f"https://api.tomorrow.io/v4/weather/realtime?location={location.lower()}&apikey={TOMORROW_API_KEY}",
            headers=headers
        )
        data = response.json()
        return f"Current weather in {location}:\n" \
            f"Temperature: {data['data']['values']['temperature']}°C,\n" \
            f"Temperature Apparent: {data['data']['values']['temperatureApparent']}°C,\n" \
            f"Humidity: {data['data']['values']['humidity']}%,"
    except Exception as e:
        return f"Error getting weather for {location}: {e}"
