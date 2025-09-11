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
    saved_bar = ft.SnackBar(
        content=ft.Text("Saved",
                        color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN
    )
    error_bar = ft.SnackBar(
        content=ft.Text("Failed to save",
                        color=ft.Colors.WHITE,
                        ),
        bgcolor=ft.Colors.RED,

    )

    def update_setting(param: str, value: int | float, bar: ft.Slider) -> None:
        if chat_state.agent:
            chat_state.agent.change_settings_params(param, value)
            bar.value = value
            page.open(saved_bar)
            page.update()
        else:
            page.open(error_bar)

    # Temperature param
    temperature_bar = ft.Slider(
        min=0.0,
        max=1.0,
        value=config.user_settings.agent_settings.temperature,
        divisions=10,
        round=1,
        label="Temperature: {value}",
        on_change=lambda e: update_setting(
            "temperature", e.control.value, temperature_bar)
    )
    # Top-k param
    top_k_bar = ft.Slider(
        min=1,
        max=100,
        value=config.user_settings.agent_settings.top_k,
        divisions=99,
        label="Top-k: {value}",
        on_change=lambda e: update_setting(
            "top_k", int(e.control.value), top_k_bar)
    )
    # Top-p param
    top_p_bar = ft.Slider(
        min=0,
        max=1,
        value=config.user_settings.agent_settings.top_p,
        divisions=10,
        round=1,
        label="Top-p: {value}",
        on_change=lambda e: update_setting("top_p", e.control.value, top_p_bar)
    )
    # Num predict param
    num_predict_bar = ft.Slider(
        min=128,
        max=1024,
        value=config.user_settings.agent_settings.num_predict,
        label="Num predict: {value}",
        on_change=lambda e: update_setting(
            "num_predict", int(e.control.value), num_predict_bar)
    )

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
                            # Settings
                            ft.Column(
                                controls=[
                                    # Temperature
                                    ft.Row(
                                        controls=[
                                            ft.Text("Model temperature:", size=14,
                                                    color=ft.Colors.WHITE,
                                                    weight=ft.FontWeight.BOLD),
                                            temperature_bar,
                                        ]
                                    ),
                                ]
                            ),
                            ft.Column(
                                controls=[
                                    # Top-k
                                    ft.Text(
                                        "Model top_k parameter:",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    top_k_bar,
                                    # Top-p
                                    ft.Text(
                                        "Model top_p parameter:",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    top_p_bar,
                                    # Num predict
                                    ft.Text(
                                        "Model num_predict parameter:",
                                        size=14,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    num_predict_bar,
                                ]
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
