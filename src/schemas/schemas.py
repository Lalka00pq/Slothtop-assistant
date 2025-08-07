import json
from pydantic import BaseModel, Field
from pathlib import Path


class AppSettings(BaseModel):
    """App settings model."""
    theme: str = Field(default="dark")


class AgentSettings(BaseModel):
    """Agent settings model."""
    name: str = Field(default="Slothtop")
    prompt: str = Field(default="You are a helpful assistant. Use the tools only if it's necessary (for example, if the user asks to open an application, you should use tools, but if the user asks a general question (for example, how are you), you can answer without using tools).")
    model: str = Field(default="llama3.2")


class UserSettings(BaseModel):
    """User settings model.

    Args:
        BaseModel (BaseModel): Base model for user settings.
    """
    app_settings: AppSettings = Field(default_factory=AppSettings)
    agent_settings: AgentSettings = Field(default_factory=AgentSettings)


class DefaultSettings(BaseModel):
    """Default settings model.

    Args:
        BaseModel (BaseModel): Base model for default settings.
    """
    app_settings: AppSettings = Field(default_factory=AppSettings)
    agent_settings: AgentSettings = Field(default_factory=AgentSettings)


class Settings(BaseModel):
    user_settings: UserSettings = Field(default_factory=UserSettings)
    default_settings: DefaultSettings = Field(default_factory=DefaultSettings)

    @classmethod
    def from_json_file(cls, file_path: str | Path) -> "Settings":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls(
            user_settings=UserSettings(**data['user_settings']),
            default_settings=DefaultSettings(**data['default_settings']),
        )
