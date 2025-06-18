import os

from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]
class Agent(api_key, model_name='mistral-large-v0.2'):
    def __init__(self):
        self.mistral = Mistral(api_key=api_key)
        self.model = 'mistral-large-v0.2'
        self.system_message = (
            "You are a helpful assistant. "
            "Answer the user's questions in a concise and informative manner."
            "If you don't know the answer, say 'I don't know'."
            "If the question is not clear, ask for clarification."
            "You should answer in Russian and shortly."
        )
    def get_response(self, question):
        chat_response = self.mistral.chat.complete(
            model=self.model,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return chat_response.choices[0].message.content