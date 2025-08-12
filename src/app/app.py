# project
from src.agent.agent import SlothAgent
from src.models.models import Models
from src.app.assets.classes import ChatState
from src.app.assets.main_page_assets import create_message_bubble
from src.app.assets.settings_page_assets import create_settings_view
from src.schemas.schemas import Settings
from src.app.assets.main_page_assets import create_main_view
# 3rd party
import flet as ft  # type: ignore


chat_state = ChatState()
config = Settings.from_json_file('src/app/settings.json')


def on_route_change(e):
    """Handle route changes between views.

    Args:
        e: Route change event
    """
    page = e.page
    page.views.clear()

    if page.route == "/settings":
        page.views.append(create_settings_view(page, chat_state))
    else:
        page.views.append(create_main_view(page, chat_state))

    page.update()


def initialize_chat_state(page: ft.Page):
    """Initialize the chat state with default values."""
    if chat_state.agent is None:
        # Initialize models
        models_handler = Models(model="llama3.2")
        try:
            available_models = models_handler.get_available_models()
            if available_models:
                default_model = available_models[0]
                try:
                    chat_state.agent = SlothAgent(llm=default_model)
                    chat_state.current_model = default_model
                except ConnectionError as e:
                    print(f"Error connecting to Ollama server: {e}")
                    chat_state.agent = None
                    chat_state.current_model = ""
                except Exception as e:
                    print(f"Error initializing agent: {e}")
            else:
                chat_state.agent = None
                chat_state.current_model = ""
        except Exception as e:
            print(f"Error fetching available models: {e}")
            chat_state.agent = None
            chat_state.current_model = ""
        # Initialize agent

        # Initialize chat container
        chat_state.chat_container = ft.Column(
            controls=[create_message_bubble(msg)
                      for msg in chat_state.messages],
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            expand=False,
            width=float('inf')
        )


def app_page(page: ft.Page):
    """Create the main application page."""
    # Basic page setup
    page.title = "AI Voice Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 20
    page.spacing = 20

    # Window setup
    page.window.width = 600
    page.window.height = 800
    page.window.min_width = 500
    page.window.min_height = 500
    page.window.left = 950
    page.window.top = 0

    # Initialize chat state
    initialize_chat_state(page)

    # Navigation setup
    page.on_route_change = on_route_change
    page.on_resized = lambda _: page.update()

    # Initialize views
    page.views.clear()
    page.views.append(create_main_view(page, chat_state))
    page.update()
