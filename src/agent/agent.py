# python
import os
# project
# from src.tools.tools import turn_of_pc, reload_pc, open_app, close_app
# 3rd party
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
# Login to Hugging Face
load_dotenv()
# os.environ["HUGGING_FACE_HUB_TOKEN"] = os.getenv("HUGGING_FACE_HUB_TOKEN")

template = """Question: {question}

Answer: Let's think step by step."""
# tools = [turn_of_pc,
#          open_app,
#          close_app,
#          reload_pc,
#          ]
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(
    model="mistral-nemo",
)
result = model.invoke("What is the capital of France?")
# chain = prompt | model
# chain.invoke({"question": "What is the capital of France?"})
print(result)
