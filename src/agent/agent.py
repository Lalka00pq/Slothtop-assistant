# python
import os
# 3rd party
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

class Agent:
    def __init__(self, api_key=api_key, model_name='mistral-small-latest'):
        self.mistral = Mistral(api_key=api_key)
        self.model = model_name
        self.system_message = (
            "You are a helpful assistant. "
            "Answer the user's questions in a concise and informative manner."
            "If you don't know the answer, say 'I don't know'."
            "If the question is not clear, ask for clarification."
            "You should answer in Russian and shortly."
        )
        self.agent = {
            "role": "system",
            "content": self.system_message
        }
    def get_response(self, question):
        chat_response = self.mistral.chat.complete(
            model=self.model,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return chat_response.choices[0].message.content