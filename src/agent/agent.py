# python
import os
# project
from src.tools.tools import turn_of_pc, reload_pc, open_app, close_app
# 3rd party
from smolagents import HfApiModel, CodeAgent, DuckDuckGoSearchTool
from huggingface_hub import login
from dotenv import load_dotenv
## Login to Hugging Face
load_dotenv()
api_key = os.getenv("HF_API_KEY")
login(token=api_key)

tools = [turn_of_pc,
         open_app,
         close_app,
         reload_pc,
         DuckDuckGoSearchTool(),
]
agent = CodeAgent(tools=tools, model=HfApiModel())
