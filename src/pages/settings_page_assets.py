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

    current_assistant_name = config.user_settings.agent_settings.name
    default_assistant_name = config.default_settings.agent_settings.name

    current_prompt = config.user_settings.agent_settings.prompt
    default_prompt = config.default_settings.agent_settings.prompt

    name_text = ft.Text(current_assistant_name, size=14, color=ft.Colors.WHITE)
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

    save_prompt_message = ft.SnackBar(
        content=ft.Text("Prompt saved successfully!",
                        color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_300,
        behavior=ft.SnackBarBehavior.FLOATING,
    )

    save_name_message = ft.SnackBar(
        content=ft.Text("Name saved successfully!",
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

    name_field = ft.TextField(
        label="Assistant name",
        hint_text="Enter new assistant name",
        width=400,
    )

    def save_name(e) -> None:
        """Save the new assistant name to the agent.

        Args:
            e : The event triggered by the button click.
        """
        if chat_state.agent and name_field.value and name_field.value.strip():
            chat_state.agent.change_prompt(
                name=name_field.value.strip(), new_prompt=current_prompt)
            page.open(save_name_message)
            nonlocal current_assistant_name
            current_assistant_name = name_field.value.strip()
            name_text.value = current_assistant_name
            name_field.value = ""
            page.update()

    def set_default_name(e) -> None:
        """Set the default assistant name.

        Args:
            e : The event triggered by the button click.
        """
        if chat_state.agent:
            chat_state.agent.change_prompt(
                name=default_assistant_name, new_prompt=current_prompt)
            name_text.value = default_assistant_name
            page.open(save_name_message)
            page.update()

    def save_prompt(e) -> None:
        """Save the new prompt to the agent.

        Args:
            e : The event triggered by the button click.
        """
        if chat_state.agent and prompt_field.value and prompt_field.value.strip():
            chat_state.agent.change_prompt(prompt_field.value.strip())
            page.open(save_prompt_message)
            nonlocal current_prompt
            current_prompt = prompt_field.value.strip()
            prompt_text.value = current_prompt
            prompt_field.value = ""
            page.update()

    def set_default_prompt(e) -> None:
        """Set the default prompt for the agent.

        Args:
            e : The event triggered by the button click.
        """
        if chat_state.agent:
            chat_state.agent.change_prompt(default_prompt)
            prompt_text.value = default_prompt
            prompt_field.value = ""
            page.update()
            page.open(save_prompt_message)

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

                            # Assistant name
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text("Assistant name:", size=14,
                                                    color=ft.Colors.WHITE,
                                                    weight=ft.FontWeight.BOLD),
                                            name_text,
                                        ]
                                    ),
                                    ft.Row(
                                        controls=[
                                            name_field,
                                            ft.ElevatedButton(
                                                text="Save",
                                                bgcolor=ft.Colors.BLUE_600,
                                                color=ft.Colors.WHITE,
                                                width=60,
                                                height=40,
                                                on_click=save_name
                                            )
                                        ]
                                    ),
                                    ft.ElevatedButton(
                                        text="Set default name",
                                        bgcolor=ft.Colors.BLUE_600,
                                        color=ft.Colors.WHITE,
                                        on_click=set_default_name
                                    )
                                ]
                            ),

                            # Prompt settings
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Current prompt:",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD
                                    ),
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
