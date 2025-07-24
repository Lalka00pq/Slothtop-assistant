
import flet as ft


def app_page(page: ft.Page):
    page.title = "AI Voice Assistant"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.SYSTEM

    page.add(
        ft.Image(src=r"src\app\Ryan.jpg",
                 width=300, height=200, fit=ft.ImageFit.CONTAIN),
        ft.Text("Welcome to the AI Voice Assistant, Jarvis!"),
        ft.Text("You can ask me about your system."),

    )
    page.add(
        ft.Row([
            ft.TextField(hint_text="How can I help you today?", width=300),
            ft.ElevatedButton("Send", on_click=lambda e: print("Clicked"),
                              icon=ft.Icons.SEND)
        ])
    )

    # ft.app(target=app_page, view=ft.AppView.FLET_APP)
