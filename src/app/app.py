import flet as ft
from datetime import datetime
from src.agent.agent import SlothAgent


class Message:
    def __init__(self, name: str, message: str, is_user: bool = True):
        self.name = name
        self.message = message
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")


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


def app_page(page: ft.Page):
    """Create the main application page.

    Args:
        page (ft.Page): The Flet page to add controls to.
    """
    page.title = "AI Voice Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 20
    page.spacing = 20
    page.window.width = 600
    page.window.height = 600
    page.window.min_width = 500
    page.window.min_height = 500
    page.window.left = 950
    page.window.top = 220
    page.on_resized = lambda _: page.update()
    sloth_agent = SlothAgent(
        llm="llama3.2",
    )

    chat_container = ft.Container(
        content=ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
            expand=False,
            width=float('inf'),
        ),
        bgcolor=ft.Colors.GREY_800,
        border_radius=ft.border_radius.all(12),
        padding=ft.padding.all(16),
        expand=True,
        border=ft.border.all(1, ft.Colors.GREY_700)

    )

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
        on_submit=lambda e: send_message(e),
        shift_enter=True
    )

    send_button = ft.ElevatedButton(
        text="Send",
        icon=ft.Icons.SEND,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        height=50,
        on_click=lambda e: send_message(e)
    )

    def send_message(e):
        """Send a message to the chat.

        Args:
            e (event): The event triggered by the send button.
        """
        if input_field.value and input_field.value.strip():
            user_message = Message(
                name="You",
                message=input_field.value.strip(),
                is_user=True
            )

            chat_container.content.controls.append(
                create_message_bubble(user_message))
            ai_message = Message(
                name="Slothtop Assistant",
                message=sloth_agent.agent_executor.invoke(
                    {"input": input_field.value.strip()})["output"],
                is_user=False
            )
            chat_container.content.controls.append(
                create_message_bubble(ai_message))

            # Clear input and update
            input_field.value = ""
            chat_container.content.scroll_to(offset=-1, duration=200)
            page.update()

            # Прокрутка к последнему сообщению

    # Main layout
    page.add(
        # Header
        ft.Container(
            content=ft.Row(
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
                alignment=ft.MainAxisAlignment.CENTER
            ),
            margin=ft.margin.only(bottom=20)
        ),

        chat_container,

        ft.Container(
            content=ft.Row(
                controls=[
                    input_field,
                    send_button
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.END
            ),
            bgcolor=ft.Colors.GREY_800,
            border_radius=ft.border_radius.all(12),
            padding=ft.padding.all(16),
            border=ft.border.all(1, ft.Colors.GREY_700)
        )
    )
