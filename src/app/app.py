
import flet as ft
# from src.agent.agent import create_agent


class Message:
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


def app_page(page: ft.Page):
    """Create the main application page.

    Args:
        page (ft.Page): The Flet page to add controls to.
    """
    chat = ft.Column()
    new_message = ft.TextField()

    def on_message(message: Message):
        """Handle incoming messages.

        Args:
            message (Message): The incoming message.
        """
        chat.controls.append(ft.Text(f"{message.name}: {message.message}"))
        page.update()

    page.pubsub.subscribe(on_message)

    def send_message(e):
        """Send a message to the chat.

        Args:
            e (event): The event triggered by the send button.
        """
        if new_message.value is not None:
            page.pubsub.send_all(
                Message(name="You", message=new_message.value))
        new_message.value = ""
        page.update()

    def send_bot_response(response: str):
        """Send a message from the bot to the chat.

        Args:
            response (str): The response message from the bot.
        """
        page.pubsub.send_all(Message(name="Bot", message=response))
        page.update()

    page.title = "AI Voice Assistant"
    page.add(
        chat,
        ft.Row(
            controls=[new_message,
                      ft.ElevatedButton(
                          text="Send",
                          on_click=send_message,
                          icon=ft.Icons.SEND
                      )],
        )
    )


ft.app(target=app_page, view=ft.AppView.FLET_APP)
