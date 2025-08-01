import requests
from typing import List


class Models:
    OLLAMA_API_URL = "http://localhost:11434"

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available models from Ollama API.

        Returns:
            List[str]: List of available model names. Empty list if no models found or API error.
        """
        try:
            response = requests.get(f"{Models.OLLAMA_API_URL}/api/tags")
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                # Extract model names from the response
                return [model["name"] for model in models_data]
            return []
        except requests.RequestException:
            return []

    def __init__(self, model: str = "llama3.2"):
        """Initialize Models class.

        Args:
            model (str, optional): Default model name. Defaults to "llama3.2".
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
