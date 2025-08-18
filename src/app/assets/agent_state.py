# project
from src.app.assets.classes import ChatState
from src.models.models import Models
from src.app.assets.classes import Message
from src.agent.agent import SlothAgent
# 3rd party
import flet as ft


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
                    content=ft.SelectionArea(
                        ft.Text(
                            message.message,
                            color=text_color,
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
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


def initialize_chat_state(chat_state: ChatState):
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
