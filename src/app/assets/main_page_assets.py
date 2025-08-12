# project
from src.app.assets.classes import Message
from src.models.models import Models
from src.app.assets.classes import ChatState
from src.voice.voice_recognition import VoiceRecognition
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


def create_main_view(page: ft.Page, chat_state: ChatState, micr_state: bool) -> ft.View:
    """Create the main chat view with all its controls.

    Returns:
        ft.View: The main chat view
    """
    # Get available models
    available_models = Models.get_available_models()

    voice_recognition = VoiceRecognition()

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
    microphone_button = ft.IconButton(
        icon=ft.Icons.MIC_OFF,
        bgcolor=ft.Colors.BLUE_600,
        on_click=lambda e: change_microphone_state(e),
    )

    def change_microphone_state(e):
        """Toggle the microphone state."""
        nonlocal micr_state
        if micr_state:
            microphone_button.icon = ft.Icons.MIC_OFF
            page.update()
            micr_state = False
            voice_recognition.stop_recording()
        else:
            microphone_button.icon = ft.Icons.MIC
            page.update()

            micr_state = True
            voice_recognition.start_recording()

        page.update()

    # Create model dropdown
    if not available_models:
        model_switch_dropdown = ft.Column(
            controls=[
                ft.Text(
                    "No models available. Please check Ollama models installation",
                    color=ft.Colors.RED_400,
                    size=14
                ),
                ft.Text(
                    "Please ensure that Ollama is running.",
                    color=ft.Colors.RED_400,
                    size=14
                )
            ]
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
        if (input_field.value and input_field.value.strip() and chat_state.agent is not None):
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
                microphone_button,
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
