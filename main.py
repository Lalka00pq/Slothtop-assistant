import os
# from src.voice.voice_recognition import record_and_transcribe
from src.agent.agent import agent
from AppOpener import open
response = agent.run("Hi can you open the Obsidian app for me?")
print(response)
# if __name__ == "__main__":
#     record_and_transcribe()
