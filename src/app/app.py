# python
from datetime import datetime
from typing import Optional
# project
from src.agent.agent import SlothAgent
from src.models.models import Models
# 3rd party
import flet as ft  # type: ignore


class Message:
    def __init__(self, name: str, message: str, is_user: bool = True):
        self.name = name
        self.message = message
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")


class ChatState:
    """Global state for the chat application."""

    def __init__(self):
        self.messages: list[Message] = []
        self.current_model: str = ""
        self.agent: Optional[SlothAgent] = None
        self.chat_container: Optional[ft.Column] = None


chat_state = ChatState()


def create_message_bubble(message: Message) -> ft.Container:
    """Create a styled message bubble for the chat.

    Args:
        message (Message): The message to display.

    Returns:
        ft.Container: A styled container with the message.
    """
    alignment = ft.CrossAxisAlignment.END if message.is_user else ft.CrossAxisAlignment.START
    bg_color = ft.Colors.BLUE_400 if message.is_user else ft.Colors.GREY_300
    text_color = ft.Colors.WHITE if message.is_user else ft.Colors.BLACK

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    message.name,
                    size=12,
                    color=ft.Colors.GREY_600,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(
                    content=ft.Text(
                        message.message,
                        color=text_color,
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                    padding=ft.padding.all(12),
                    border_radius=ft.border_radius.all(12),
                    bgcolor=bg_color,
                    margin=ft.margin.only(bottom=4)
                ),
                ft.Text(
                    message.timestamp,
                    size=10,
                    color=ft.Colors.GREY_500
                )
            ],
            horizontal_alignment=alignment,
            spacing=2
        ),
        margin=ft.margin.only(bottom=16),
        width=float('inf')
    )


def create_settings_view(page: ft.Page) -> ft.View:
    """Create the settings view with all its controls.

    Returns:
        ft.View: The settings view
    """
    # Header with back button
    header = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.BLUE_400,
                on_click=lambda _: page.go("/")
            ),
            ft.Text(
                "Settings",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
        ],
        alignment=ft.MainAxisAlignment.START
    )

    # Settings content
    settings_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Application Settings",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                # Theme settings
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Theme", size=16, color=ft.Colors.WHITE),
                            ft.Switch(
                                label="Dark Mode",
                                value=True,
                                active_color=ft.Colors.BLUE_400
                            ),
                        ],
                    ),
                    padding=10,
                ),
                # Model settings
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Models settings", size=16,
                                    color=ft.Colors.WHITE),
                            ft.TextField(
                                label="New prompt",
                                hint_text="Enter new prompt",
                                width=400,
                                multiline=True,
                                shift_enter=True
                            ),
                        ],
                    ),
                    padding=10,
                ),
            ],
            spacing=20
        ),
        padding=ft.padding.all(16),
        bgcolor=ft.Colors.GREY_800,
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(1, ft.Colors.GREY_700)
    )

    # Combine all elements in a view
    return ft.View(
        route="/settings",
        controls=[
            header,
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            settings_content
        ],
        bgcolor=ft.Colors.GREY_900,
        padding=ft.padding.all(16),
        spacing=20
    )


def create_main_view(page: ft.Page) -> ft.View:
    """Create the main chat view with all its controls.

    Returns:
        ft.View: The main chat view
    """
    # Get available models
    models_handler = Models(model="llama3.2")
    available_models = models_handler.get_available_models()

    # Create chat container using global state
    chat_container = ft.Container(
        content=chat_state.chat_container,
        bgcolor=ft.Colors.GREY_800,
        border_radius=ft.border_radius.all(12),
        padding=ft.padding.all(16),
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_700)
    )

    # Create input field
    input_field = ft.TextField(
        hint_text="How can I help you today?",
        border_radius=ft.border_radius.all(25),
        bgcolor=ft.Colors.GREY_800,
        border_color=ft.Colors.GREY_600,
        focused_border_color=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE,
        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=5,
        shift_enter=True
    )

    # Create send button
    send_button = ft.ElevatedButton(
        text="Send",
        icon=ft.Icons.SEND,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        height=50
    )

    # Create model dropdown
    if not available_models:
        model_switch_dropdown = ft.Text(
            "No models available. Please check Ollama installation.",
            color=ft.Colors.RED_400,
            size=14
        )
    else:
        model_switch_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(model_name, model_name.capitalize())
                for model_name in available_models
            ],
            width=150,
            text_size=14,
            label="Select Model",
            value=chat_state.current_model
        )

    def send_message(e):
        """Send a message to the chat."""
        if input_field.value and input_field.value.strip():
            # Create and save user message
            user_message = Message(
                name="You",
                message=input_field.value.strip(),
                is_user=True
            )
            chat_state.messages.append(user_message)

            # Update UI with user message
            if chat_state.chat_container:
                chat_state.chat_container.controls.append(
                    create_message_bubble(user_message))
                chat_state.chat_container.scroll_to(
                    offset=-1, duration=200)
                page.update()

            # Clear input and get response
            text = input_field.value.strip()
            input_field.value = ""
            page.update()

            # Create and save AI message
            if chat_state.agent:
                ai_message = Message(
                    name="Slothtop Assistant",
                    message=chat_state.agent.invoke_agent(text)["output"],
                    is_user=False
                )
                chat_state.messages.append(ai_message)

                # Update UI with AI message
                if chat_state.chat_container:
                    chat_state.chat_container.controls.append(
                        create_message_bubble(ai_message))
                    chat_state.chat_container.scroll_to(
                        offset=-1, duration=200)
                    page.update()

    def model_switch(e):
        """Switch the model used by the SlothAgent."""
        new_model = str(e.control.value)
        if chat_state.agent:
            chat_state.agent.change_llm(new_llm=new_model)
            chat_state.current_model = new_model
            print(f"Model changed to: {new_model}")
            page.update()

    # Bind event handlers
    input_field.on_submit = send_message
    send_button.on_click = send_message
    if isinstance(model_switch_dropdown, ft.Dropdown):
        model_switch_dropdown.on_change = model_switch

    # Create header with settings button
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=ft.Colors.BLUE_400,
                    tooltip="Settings",
                    on_click=lambda _: page.go("/settings")
                ),
                ft.Row(
                    controls=[
                        ft.Image(
                            src=r"src\app\sloth_5980972.png",
                            width=50,
                            height=50,
                            color=ft.Colors.BLUE_600,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Text(
                                "Image not found", color=ft.Colors.RED_400),
                        ),
                        ft.Text(
                            "Slothtop Assistant",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        margin=ft.margin.only(bottom=20)
    )

    # Create input container
    input_container = ft.Container(
        content=ft.Row(
            controls=[
                input_field,
                send_button,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.END
        ),
        bgcolor=ft.Colors.GREY_800,
        border_radius=ft.border_radius.all(12),
        padding=ft.padding.all(16),
        border=ft.border.all(1, ft.Colors.GREY_700)
    )

    # Create model selector container
    model_selector = ft.Container(
        content=ft.Row(
            controls=[
                model_switch_dropdown,
            ],
            alignment=ft.MainAxisAlignment.START
        ),
        bgcolor=ft.Colors.GREY_900,
        padding=ft.padding.all(12),
        border_radius=ft.border_radius.all(12)
    )

    # Return the main view with all components
    return ft.View(
        route="/",
        controls=[
            header,
            chat_container,
            input_container,
            model_selector
        ],
        bgcolor=ft.Colors.GREY_900,
        padding=ft.padding.all(16),
        spacing=20
    )


def on_route_change(e):
    """Handle route changes between views.

    Args:
        e: Route change event
    """
    page = e.page
    page.views.clear()

    if page.route == "/settings":
        page.views.append(create_settings_view(page))
    else:
        page.views.append(create_main_view(page))

    page.update()


def initialize_chat_state(page: ft.Page):
    """Initialize the chat state with default values."""
    if chat_state.agent is None:
        # Initialize models
        models_handler = Models(model="llama3.2")
        available_models = models_handler.get_available_models()
        default_model = available_models[0] if available_models else "llama3.2"

        # Initialize agent
        chat_state.agent = SlothAgent(llm=default_model)
        chat_state.current_model = default_model

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
    page.views.append(create_main_view(page))
    page.update()
