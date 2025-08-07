# python
from datetime import datetime
from typing import Optional
# project
from src.agent.agent import SlothAgent
# 3rd party
import flet as ft


class Message:
    def __init__(self, name: str, message: str, is_user: bool = True):
        self.name = name
        self.message = message
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")


class ChatState:
    """Global state for the chat application."""

    def __init__(self):
        self.messages: list[Message] = []
        self.current_model: str = ""
        self.agent: Optional[SlothAgent] = None
        self.chat_container: Optional[ft.Column] = None
