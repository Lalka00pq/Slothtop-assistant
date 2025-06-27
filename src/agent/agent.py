# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool, multiply_tool
from src.tools.web_work_tools import search_web_tool
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool


def create_agent(tools: list[BaseTool] = None) -> AgentExecutor:
    """Creates an agent for interacting with the user and performing tasks.

    Returns:
        AgentExecutor: The agent executor instance.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the tools provided to answer the user's questions. For example, if the user asks to open an application, use the open_app_tool. If they ask to close an application, use the close_app_tool. If they ask to turn off or restart the PC, use the turn_off_pc_tool or restart_pc_tool respectively.\n"
         "If you cannot answer, say 'I don't know'."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    tools = [
        open_app_tool,
        close_app_tool,
        turn_off_pc_tool,
        restart_pc_tool,
        multiply_tool,
        search_web_tool
    ]
    llm = OllamaLLM(
        model="mistral-nemo"
    )
    llm = llm.bind_tools(tools)
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
