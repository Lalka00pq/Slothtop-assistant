# project
from src.agent.agent import create_agent
from src.voice.voice_recognition import record_and_transcribe
from src.app.app import app_page
# 3rd party
import flet as ft


def main() -> None:
    """Main function to create the agent and invoke it with a sample input."""

    agent = create_agent()

    result = agent.invoke(
        {"input": "What can you say me about the langchain framework?"})

    print(result['output'] if 'output' in result else 'No result')


if __name__ == "__main__":
    # record_and_transcribe()
    # main()
    ft.app(target=app_page, view=ft.AppView.FLET_APP)
