# python
from typing import Optional
# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool
from src.tools.web_work_tools import tavily_web_search_tool
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool


class SlothAgent:
    def __init__(self, llm: str = "llama3.2", tools_list: Optional[list[BaseTool]] = None):
        """Initialize the SlothAgent with a language model and a list of tools.

        Args:
            llm (str, optional): The language model to use for the agent.
            tools_list (Optional[list[BaseTool]], optional): A list of tools the agent can use. Defaults to None.

        Returns:
            None: None
        """
        self.tools = tools_list or [
            # open_app_tool,
            # close_app_tool,
            # turn_off_pc_tool,
            # restart_pc_tool,
            # tavily_web_search_tool
        ]
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the tools only if it's necessary (for example, if the user asks to open an application, you should use tools, but if the user asks a general question, you can answer without using tools)."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        self.llm = OllamaLLM(model=llm)
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True
        )

        def invoke_agent(self, query: str) -> dict:
            """Invoke the agent with the given input text.
            Args:
                query (str): The input text to process.

            Returns:
                dict: The agent's response.
            """
            return self.agent_executor.invoke({"input": query})

        def change_llm(self, new_llm: str) -> None:
            """Change the language model used by the agent.

            Args:
                new_llm (str): The new language model to use.
            """
            self.llm = OllamaLLM(model=new_llm)
            self.agent = create_tool_calling_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True
            )
