# project
from src.app.app import app_page
from src.agent.agent import SlothAgent
# 3rd party
import flet as ft


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""
    ft.app(target=app_page, view=ft.AppView.FLET_APP)


if __name__ == "__main__":
    main()
