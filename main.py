# project
# from src.voice.voice_recognition import record_and_transcribe
from src.agent.agent import create_agent
agent = create_agent()
result = agent.invoke({"input": "Can you open Obsidian?", })

# if __name__ == "__main__":
#     record_and_transcribe()
