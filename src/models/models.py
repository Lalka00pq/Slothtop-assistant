# python
import requests
from typing import List
# 3rd party
import ollama


class Models:
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available models from Ollama API.

        Returns:
            List[str]: List of available model names. Empty list if no models found or API error.
        """
        try:
            models = ollama.list()
            return [model.model for model in models.models if model.model]
        except requests.RequestException as e:
            print(f"Warning: Could not connect to Ollama API: {e}")
            return []
        except Exception as e:
            print(f"Warning: Unexpected error while fetching models: {e}")
            return []

    def __init__(self, model: str):
        """Initialize Models class.

        Args:
            model (str): Default model name. Defaults to "llama3.2".
        """
        self.model = model
        self.available_models = self.get_available_models()

    def is_model_available(self, model_name: str) -> bool:
        """Check if specified model is available.

        Args:
            model_name (str): Name of the model to check

        Returns:
            bool: True if model is available, False otherwise
        """
        return model_name in self.available_models

    def refresh_models(self) -> None:
        """Refresh the list of available models."""
        self.available_models = self.get_available_models()
