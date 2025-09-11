import json
from pydantic import BaseModel, Field
from pathlib import Path


class AppSettings(BaseModel):
    """App settings model."""
    theme: str = Field(default="dark")


class AgentSettings(BaseModel):
    """Agent settings model."""
    temperature: float = Field(default=0.7)
    default_model: str = Field(default="llama3.2")
    prompt: str = Field(
        default="You are a helpful assistant, you should use tools to help users with their tasks. If user just chat with you, you should stop this chat and say that you are a tool-using assistant.")
    num_predict: int = Field(default=128)
    top_k: int = Field(default=40)
    top_p: float = Field(default=0.95)


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
