# python
from typing import Optional
import requests
# project
from src.tools.tools import open_app_tool, close_app_tool, turn_off_pc_tool, restart_pc_tool
from src.tools.monitoring_tools.monitoring_tool import start_monitoring_cpu_tool, stop_monitoring_cpu_tool, start_monitoring_gpu_tool, stop_monitoring_gpu_tool
from src.tools.web_work_tools import tavily_web_search_tool
from src.schemas.schemas import Settings
# 3rd party
from langchain_ollama.chat_models import ChatOllama as OllamaLLM  # type: ignore
from langchain.agents import create_tool_calling_agent, AgentExecutor  # type: ignore
from langchain_core.prompts import ChatPromptTemplate  # type: ignore
from langchain_core.tools import BaseTool  # type: ignore
from langchain.memory import ConversationBufferMemory  # type: ignore
from langchain.prompts import MessagesPlaceholder  # type: ignore

# settings
config = Settings.from_json_file('src/app/settings.json')


class SlothAgent:
    def __init__(self, llm: str = config.user_settings.agent_settings.model, tools_list: Optional[list[BaseTool]] = None):
        """Initialize the SlothAgent with a language model and a list of tools.

        Args:
            llm (str): The language model to use for the agent.
            tools_list (Optional[list[BaseTool]], optional): A list of tools the agent can use. Defaults to None.

        Returns:
            None: None
        """
        self.tools = tools_list or [
            # open_app_tool,
            # close_app_tool,
            # turn_off_pc_tool,
            # restart_pc_tool,
            # tavily_web_search_tool,
            # start_monitoring_cpu_tool,
            # stop_monitoring_cpu_tool,
            # start_monitoring_gpu_tool,
            # stop_monitoring_gpu_tool
        ]
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", config.user_settings.agent_settings.prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        self.llm = OllamaLLM(model=llm)
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input"
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )

    def invoke_agent(self, query: str) -> dict:
        """Invoke the agent with the given input text.
        Args:
            query (str): The input text to process.

        Returns:
            dict: The agent's response.
        """
        response = self.agent_executor.invoke({"input": query})
        return response

    def check_ollama_connection(self) -> bool:
        """Check if Ollama server is running and accessible.

        Returns:
            bool: True if Ollama server is running and accessible, False otherwise.
        """
        try:
            # Try to connect to the Ollama API
            response = requests.get(
                "http://localhost:11434")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(
                f"Error connecting to Ollama server: {e} Please check if Ollama server is running.")
            return False

    def change_llm(self, new_llm: str) -> None:
        """Change the language model used by the agent.

        Args:
            new_llm (str): The new language model to use.
        """
        try:
            self.llm = OllamaLLM(model=new_llm)
        except Exception as e:
            print(f"Error changing LLM: {e} - using default LLM.")
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )

    def change_prompt(self, new_prompt: str) -> None:
        """Change the prompt used by the agent.

        Args:
            new_prompt (str): The new prompt to use.
        """
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", new_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory
        )
