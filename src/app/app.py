# project
from src.schemas.classes import ChatState
from src.pages.settings_page_assets import create_settings_view
from src.schemas.schemas import Settings
from src.pages.main_page_assets import create_main_view
from src.agent.agent_state import initialize_chat_state
# 3rd party
import flet as ft


chat_state = ChatState()
config = Settings.from_json_file('src/app/settings.json')
micr_state = False


def on_route_change(e) -> None:
    """Handle route changes between views.

    Args:
        e: Route change event
    """
    page = e.page
    page.views.clear()

    if page.route == "/settings":
        page.views.append(create_settings_view(page, chat_state))
    else:
        page.views.append(create_main_view(page, chat_state, micr_state))

    page.update()


def app_page(page: ft.Page) -> None:
    """Create the main application page."""
    # Basic page setup
    page.title = "AI Voice Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 20
    page.spacing = 20

    # Window setup
    page.window.width = 800
    page.window.height = 800
    page.window.min_width = 500
    page.window.min_height = 500
    page.window.center()

    # Initialize chat state
    initialize_chat_state(chat_state=chat_state)

    # Navigation setup
    page.on_route_change = on_route_change
    page.on_resized = lambda _: page.update()

    # Initialize views
    page.views.clear()
    page.views.append(create_main_view(page, chat_state, micr_state))
    page.update()
