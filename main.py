import os
# from src.voice.voice_recognition import record_and_transcribe
from src.agent.agent import Agent
api_key = os.getenv("MISTRAL_API_KEY")
agent = Agent(api_key)
response = agent.get_response("Какой сегодня день?")
print(response)
# if __name__ == "__main__":
#     record_and_transcribe()
