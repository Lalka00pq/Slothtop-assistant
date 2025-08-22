# project
from src.schemas.classes import ChatState
from src.schemas.schemas import Settings
# 3rd party
import flet as ft


def create_settings_view(page: ft.Page, chat_state: ChatState) -> ft.View:
    """Create the settings view with all its controls.

    Returns:
        ft.View: The settings view
    """
    config = Settings.from_json_file('src/app/settings.json')
    current_prompt = config.user_settings.agent_settings.prompt
    default_prompt = config.default_settings.agent_settings.prompt
    prompt_text = ft.Text(current_prompt, size=14, color=ft.Colors.WHITE)
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

    save_message = ft.SnackBar(
        content=ft.Text("Prompt saved successfully!",
                        color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_300,
        behavior=ft.SnackBarBehavior.FLOATING,
    )

    # Settings content
    prompt_field = ft.TextField(
        label="New prompt",
        hint_text="Enter new prompt",
        width=400,
        multiline=True,
        shift_enter=True
    )

    def save_prompt(e):
        """Save the new prompt to the agent.

        Args:
            e : The event triggered by the button click.
        """
        if chat_state.agent and prompt_field.value and prompt_field.value.strip():
            chat_state.agent.change_prompt(prompt_field.value.strip())
            page.open(save_message)
            nonlocal current_prompt
            current_prompt = prompt_field.value.strip()
            prompt_text.value = current_prompt
            prompt_field.value = ""
            page.update()

    def set_default_prompt(e):
        """Set the default prompt for the agent."""
        if chat_state.agent:
            chat_state.agent.change_prompt(default_prompt)
            prompt_text.value = default_prompt
            prompt_field.value = ""
            page.update()
            page.open(save_message)

    settings_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Application Settings:",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                ),
                # Theme settings
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Theme (in development)",
                                    size=16, color=ft.Colors.WHITE),
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
                            ft.Text("Models settings:", size=20,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Current prompt:", size=14, color=ft.Colors.WHITE),
                                    prompt_text
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    prompt_field,
                                    ft.ElevatedButton(
                                        text="Save",
                                        bgcolor=ft.Colors.BLUE_600,
                                        color=ft.Colors.WHITE,
                                        width=60,
                                        height=40,
                                        on_click=save_prompt
                                    )
                                ]
                            ),
                            ft.ElevatedButton(
                                text='Set default prompt',
                                on_click=set_default_prompt,
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE
                            )
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
