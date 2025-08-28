# project
import flet as ft
from src.schemas.classes import Message, ChatState
from src.models.models import Models
from src.voice.voice_recognition import VoiceRecognition
from src.agent.agent_state import initialize_chat_state, create_message_bubble
from src.schemas.schemas import Settings

# settings
config = Settings.from_json_file('src/app/settings.json')
# 3rd party


def create_main_view(page: ft.Page, chat_state: ChatState, micr_state: bool) -> ft.View:
    """Create the main chat view with all its controls.

    Returns:
        ft.View: The main chat view
    """
    # Get available models
    available_models = Models.get_available_models()

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

    # Sending message
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

    microphone_on_message = ft.SnackBar(
        content=ft.Text(
            "Microphone enabled. You can say your command", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_300,
        behavior=ft.SnackBarBehavior.FLOATING,
    )
    microphone_off_message = ft.SnackBar(
        content=ft.Text(
            "Microphone disabled.", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_300,
        behavior=ft.SnackBarBehavior.FLOATING,
    )

    def process_voice_input(transcribed_text: str) -> None:
        """Process the transcribed voice input.

        Args:
            transcribed_text (str): The transcribed voice input text.
        """
        if chat_state.agent is not None:
            user_message = Message(
                name="You",
                message=transcribed_text,
                is_user=True
            )
            chat_state.messages.append(user_message)

            if chat_state.chat_container:
                chat_state.chat_container.controls.append(
                    create_message_bubble(user_message))
                chat_state.chat_container.scroll_to(
                    offset=-1, duration=200)
                page.update()

            ai_message = Message(
                name=config.user_settings.agent_settings.name,
                message=chat_state.agent.invoke_agent(
                    transcribed_text)["output"],
                is_user=False
            )
            chat_state.messages.append(ai_message)

            if chat_state.chat_container:
                chat_state.chat_container.controls.append(
                    create_message_bubble(ai_message))
                chat_state.chat_container.scroll_to(
                    offset=-1, duration=200)
                page.update()

    def reconnect_to_ollama(e) -> None:
        """Attempt to reconnect to Ollama service.

        Args:
            e : The event triggered by the button click.
        """
        reconnect_progress = ft.ProgressRing(
            width=16,
            height=16,
            stroke_width=2,
            color=ft.Colors.BLUE_400,
        )
        e.control.content.controls[0] = reconnect_progress
        e.control.content.controls[1].value = "Connecting..."
        page.update()

        # Try to reconnect to Ollama
        try:
            initialize_chat_state(chat_state=chat_state)
            if chat_state.agent is not None:
                page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            "Successfully connected to Ollama!",
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=ft.Colors.GREEN_400,
                        action="OK",
                    )
                )
            else:
                page.open(
                    ft.SnackBar(
                        content=ft.Text(
                            "Failed to connect to Ollama.",
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=ft.Colors.RED_400,
                        action="OK",
                    )
                )
            page.views.clear()
            page.views.append(create_main_view(page, chat_state, micr_state))

        except Exception as err:
            page.open(
                ft.SnackBar(
                    content=ft.Text(
                        f"Failed to connect: {str(err)}",
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.RED_400,
                    action="OK",
                )
            )
            e.control.content.controls[0] = ft.Icon(
                name=ft.Icons.REFRESH_ROUNDED,
                color=ft.Colors.WHITE,
            )
            e.control.content.controls[1].value = "Reconnect to Ollama"

        page.update()

    voice_recognition = VoiceRecognition(
        on_transcribe_callback=process_voice_input
    )

    def change_microphone_state(e) -> None:
        """Toggle the microphone state.

        Args:
            e : The event triggered by the button click.
        """
        nonlocal micr_state
        if micr_state:
            microphone_button.icon = ft.Icons.MIC_OFF
            page.open(microphone_off_message)
            page.update()
            micr_state = False
            voice_recognition.stop_recording()
        else:
            microphone_button.icon = ft.Icons.MIC
            page.open(microphone_on_message)
            page.update()

            micr_state = True
            voice_recognition.start_recording()

        page.update()

    # Create model dropdown
    if not available_models:
        model_switch_dropdown = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.ERROR_OUTLINE,
                                color=ft.Colors.RED_400,
                                size=24,
                            ),
                            ft.Text(
                                "Connection to Ollama failed",
                                color=ft.Colors.RED_400,
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        "Please ensure that Ollama service is running",
                        color=ft.Colors.GREY_400,
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        name=ft.Icons.REFRESH_ROUNDED,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "Reconnect to Ollama",
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: reconnect_to_ollama(e),
                            height=45,
                        ),
                        margin=ft.margin.only(top=10),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                expand=True,
                width=float('inf'),
            ),
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.Colors.RED_400),
            border_radius=ft.border_radius.all(12),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED_400),
            expand=True,
            width=float('inf'),
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

    def send_message(e) -> None:
        """Send a message to the chat.

        Args:
            e : The event triggered by the button click.
        """
        if (input_field.value and input_field.value.strip() and chat_state.agent is not None):
            text = input_field.value.strip()
            input_field.value = ""

            user_message = Message(
                name="You",
                message=text,
                is_user=True
            )
            chat_state.messages.append(user_message)

            if chat_state.chat_container:
                chat_state.chat_container.controls.append(
                    create_message_bubble(user_message)
                )
                chat_state.chat_container.scroll_to(offset=-1, duration=200)
                page.update()

            thinking_message = Message(
                name=config.user_settings.agent_settings.name,
                message="🦥 Thinking...",
                is_user=False
            )
            thinking_container = create_message_bubble(thinking_message)

            if chat_state.chat_container:
                chat_state.chat_container.controls.append(thinking_container)
                chat_state.chat_container.scroll_to(offset=-1, duration=200)
                page.update()

            if chat_state.agent:
                response = chat_state.agent.invoke_agent(text)

                if 'thoughts' in response and response['thoughts']:
                    for thought in response['thoughts']:
                        thinking_message.message = f"🦥 {thought['thought']}\n📝 {thought['observation']}"
                        page.update()

                ai_message = Message(
                    name=config.user_settings.agent_settings.name,
                    message=response["output"],
                    is_user=False
                )

                if chat_state.chat_container:
                    chat_state.chat_container.controls.remove(
                        thinking_container)
                    chat_state.chat_container.controls.append(
                        create_message_bubble(ai_message)
                    )
                    chat_state.messages.append(ai_message)
                    chat_state.chat_container.scroll_to(
                        offset=-1, duration=200)
                    page.update()

    def model_switch(e) -> None:
        """Switch the model used by the SlothAgent.

        Args:
            e : The event triggered by the dropdown change.
        """
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
                            src=r"src\assets\sloth_5980972.png",
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
